%
%--------------------------------------------------------------%
% copybytes                                                    %
%--------------------------------------------------------------%
% Copy n words from the source stack pointer to the destination stack pointer.
% Both pointers should point to the end of each memory space.
% It uses registers r1 to r3 as inputs and r4 to r5 as temp.
% Branch to this subroutine using r10, *NOT* r15
% inputs:
%   r1 -> source address
%   r2 -> destination address
%   r3 -> number of words to copy
% output:
%   None

copywords   align
copywords1  cgt     r4, r3, r0
            bz      r4, copywords2  % Copying is finished
            lw      r5, -4(r1)       % Copy the word
            sw      -4(r2), r5
            subi    r3, r3, 1       % Update r1, r2, r3
            subi    r1, r1, 4
            subi    r2, r2, 4
            j       copywords1
copywords2  jr      r10
