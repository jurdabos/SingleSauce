Here I will document the high-level architecture,
including how local/remote DB synchronization works, so newcomers can quickly grasp the system design.

I will include  short description of the data flow:
user → local DB → sync service → remote DB → back end for multi-user sync.

