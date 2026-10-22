/* Controlled kernel workload and bounded-history tests for the monitor. */
#include "tests/threads/tests.h"
#include <debug.h>
#include <stdio.h>
#include <string.h>
#include "devices/timer.h"
#include "threads/interrupt.h"
#include "threads/synch.h"
#include "threads/thread.h"

#define WORKERS 3
struct worker_data
  {
    const char *name;
    int units;
    int yields_per_unit;
    tid_t tid;
    struct semaphore gate;
    bool initialized;
    bool blocked_ok;
    bool monotonic;
    struct thread_monitor_record before_work;
    struct thread_monitor_record after_work;
  };

/* Static test storage avoids large arrays on the 4 KB kernel stack. */
static struct worker_data workers[WORKERS];
static struct thread_monitor_record records[THREAD_MONITOR_CAPACITY];
static struct semaphore ready;
static struct semaphore done;

static void
worker (void *aux)
{
  struct worker_data *data = aux;
  struct thread_monitor_record before, after;
  enum intr_level old_level;
  int i, j;

  /* Snapshot immediately before blocking and after resumption with no
     enabled-interrupt execution in between on this thread. */
  old_level = intr_disable ();
  thread_monitor_current (&before);
  data->initialized = before.tid == thread_tid () && before.dispatches > 0;
  sema_up (&ready);
  sema_down (&data->gate);
  thread_monitor_current (&after);
  data->blocked_ok = before.cpu_ticks == after.cpu_ticks &&
                     after.dispatches > before.dispatches;
  intr_set_level (old_level);

  thread_monitor_current (&data->before_work);
  for (i = 0; i < data->units; i++)
    {
      timer_mdelay (25);                /* Real calibrated CPU work. */
      for (j = 0; j < data->yields_per_unit; j++)
        thread_yield ();
    }
  thread_monitor_current (&data->after_work);
  data->monotonic = data->after_work.cpu_ticks >= data->before_work.cpu_ticks &&
                    data->after_work.dispatches >= data->before_work.dispatches
                    + data->units * data->yields_per_unit;
  sema_up (&done);
  /* Returning invokes thread_exit(), which records the final counters. */
}

static bool
has_record (tid_t tid)
{
  size_t i, count = thread_monitor_snapshot (records, THREAD_MONITOR_CAPACITY, NULL);
  for (i = 0; i < count; i++)
    if (records[i].tid == tid)
      return true;
  return false;
}

/* A completion semaphore may wake the controller before thread_exit().
   Wait for the actual kernel completion record, not just the semaphore. */
static void
wait_for_exit (tid_t tid)
{
  int64_t deadline = timer_ticks () + 2 * TIMER_FREQ;
  while (!has_record (tid))
    {
      if (timer_ticks () >= deadline)
        fail ("Timed out waiting for completion record %d", tid);
      thread_yield ();
    }
}

void
test_cpu_monitor (void)
{
  static const char *names[WORKERS] = {"worker-a", "worker-b", "worker-c"};
  static const int units[WORKERS] = {8, 4, 1};
  uint64_t overwritten;
  size_t count, k;
  int i, j;

  ASSERT (!thread_mlfqs);
  msg ("Monitor v1: CPU-heavy, yielding, and initially blocked workers.");
  msg ("struct thread=%u bytes; history capacity=%u",
       (unsigned) sizeof (struct thread), THREAD_MONITOR_CAPACITY);
  sema_init (&ready, 0);
  sema_init (&done, 0);
  memset (workers, 0, sizeof workers);
  for (i = 0; i < WORKERS; i++)
    {
      workers[i].name = names[i];
      workers[i].units = units[i];
      workers[i].yields_per_unit = i == 1 ? 10 : 0;
      sema_init (&workers[i].gate, 0);
      workers[i].tid = thread_create (names[i], PRI_DEFAULT, worker, &workers[i]);
      if (workers[i].tid == TID_ERROR)
        fail ("Worker creation failed");
      msg ("Created %s tid=%d units=%d yields-per-unit=%d",
           names[i], workers[i].tid, units[i], workers[i].yields_per_unit);
      for (j = 0; j < i; j++)
        ASSERT (workers[j].tid != workers[i].tid);
    }
  for (i = 0; i < WORKERS; i++)
    sema_down (&ready);
  timer_mdelay (30);                    /* All workers are truly blocked. */
  for (i = 0; i < WORKERS; i++)
    sema_up (&workers[i].gate);
  for (i = 0; i < WORKERS; i++)
    sema_down (&done);
  for (i = 0; i < WORKERS; i++)
    wait_for_exit (workers[i].tid);

  count = thread_monitor_snapshot (records, THREAD_MONITOR_CAPACITY, &overwritten);
  ASSERT (count == WORKERS && overwritten == 0);
  for (i = 0; i < WORKERS; i++)
    {
      int matches = 0;
      ASSERT (workers[i].initialized && workers[i].blocked_ok && workers[i].monotonic);
      for (k = 0; k < count; k++)
        if (records[k].tid == workers[i].tid)
          {
            matches++;
            ASSERT (!strcmp (records[k].name, workers[i].name));
            ASSERT (records[k].priority == PRI_DEFAULT);
            ASSERT (records[k].status == THREAD_DYING);
            ASSERT (records[k].dispatches > 0);
            ASSERT (records[k].cpu_ticks >= workers[i].after_work.cpu_ticks);
            ASSERT (records[k].dispatches >= workers[i].after_work.dispatches);
          }
      ASSERT (matches == 1);
    }
  if (!thread_monitor_report ())
    fail ("Could not allocate bounded report buffer");
  msg ("PASS: initialized IDs/counters, no blocked ticks, monotonic counters");
  msg ("PASS: exactly one final record per worker after thread destruction");
  msg ("PASS: dispatches include every voluntary yield return");
  pass ();
}

static void
short_worker (void *aux UNUSED)
{
  sema_up (&done);
}

void
test_monitor_overflow (void)
{
  static tid_t ids[THREAD_MONITOR_CAPACITY + 3];
  struct thread_monitor_record one;
  uint64_t overwritten;
  size_t count, i, j;

  sema_init (&done, 0);
  for (i = 0; i < THREAD_MONITOR_CAPACITY + 3; i++)
    {
      ids[i] = thread_create ("history-worker", PRI_DEFAULT, short_worker, NULL);
      ASSERT (ids[i] != TID_ERROR);
      sema_down (&done);
      wait_for_exit (ids[i]);
    }
  count = thread_monitor_snapshot (records, THREAD_MONITOR_CAPACITY, &overwritten);
  ASSERT (count == THREAD_MONITOR_CAPACITY && overwritten == 3);
  for (i = 0; i < count; i++)
    {
      ASSERT (records[i].tid == ids[i + 3]);
      ASSERT (records[i].status == THREAD_DYING && records[i].dispatches > 0);
      for (j = 0; j < i; j++)
        ASSERT (records[i].tid != records[j].tid);
    }
  ASSERT (thread_monitor_snapshot (&one, 1, NULL) == 1);
  ASSERT (one.tid == ids[THREAD_MONITOR_CAPACITY + 2]);
  ASSERT (thread_monitor_snapshot (NULL, 0, &overwritten) == 0);
  ASSERT (overwritten == 3);
  msg ("PASS: newest %u records retained, 3 oldest overwritten", THREAD_MONITOR_CAPACITY);
  msg ("PASS: bounded and zero-capacity snapshots");
  pass ();
}
