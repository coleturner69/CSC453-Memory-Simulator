CSC 453 Project 3: Designing a virtual memory manager
By: Cole Turner, Kenneth Choi, Logan Schwarz

For optimal PRA, in the case where no frames from the current memory are used again in the future, 
the 0 index frame is replaced. There is no reason to implement another structure to further break
ties since none of those frames are ever used again and can be replaced. 
