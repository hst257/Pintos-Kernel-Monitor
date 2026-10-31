
# Video Walkthrough & Team Participation Mapping

**Course:** BCSE303L - Operating Systems  
**Mini Project:** Modifying a Small OS Kernel  
**Team Name:** Group HarshMesh  
**Project Title:** Pintos Kernel — Per-Thread CPU Monitoring and Scheduling Analytics  

---

## 1. Video Recording Link
* **Google Drive Link:** https://drive.google.com/file/d/1ys3eYd0nnoiFSu2oZJ9JKpeVbJnOLfJB/view?usp=sharing

---

## 2. Team Member Timestamp Mapping

| Team Member | Registration No. | Timestamp Range | Topics Covered in Walkthrough |
| :--- | :--- | :--- | :--- |
| **Harshit Sharma Thakur** | 24BCE0437 | `00:00 – 08:47` | OS Selection rationale; Baseline boot verification in QEMU; Modern GCC PIC/PIE boot flags resolution; Kernel source modifications in `thread.h` and `thread.c` (`thread_tick`, `schedule`, and `thread_exit`). |
| **Prathamesh Chalak** | 24BCT0286 | `08:47 – 15:18` | Independent source build verification (`setup_person2.sh`); Live demonstration (`demo_person2.sh`); CPU ticks vs. Dispatches empirical analysis; 16-entry history buffer overflow test; Regression tests & `priority-fifo` limitation discussion. |

---

## 3. Walkthrough Outline

### Part 1: Harshit Sharma Thakur (24BCE0437) — [00:00 – 08:47]
* Architecture overview of Pintos and the motivation for per-thread analytics.
* Unmodified baseline build, QEMU boot verification, and solving modern toolchain resets.
* Implementation details of per-thread data structures, timer accounting in `thread_tick()`, scheduler dispatch counting in `schedule()`, and safe termination memory preservation in `thread_exit()`.

### Part 2: Prathamesh Chalak (24BCT0286) — [08:47 – 15:18]
* Independent compilation and setup confirmation from clean source.
* Live demonstration showing 5/5 passing tests.
* Comparative breakdown: Worker A (compute-heavy, 20 ticks, 7 dispatches) vs. Worker B (yielding, 10 ticks, 42 dispatches).
* Ring buffer verification with 19 completed threads and timer regression suite validation (`alarm-single`, `alarm-simultaneous`, `alarm-zero`).
* Transparent discussion of the upstream `priority-fifo` limitation and single-core assumptions.
