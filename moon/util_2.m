%
%--------------------------------------------------------------%
% copybytes                                                    %
%--------------------------------------------------------------%
% Copy n bytes from the source to the destination
% inputs:
%   r1 -> source address
%   r2 -> destination address
%   r3 -> number of bytes to copy
% output:
%   None

copybytes   align
copybytes1  cgt     r4, r3, r0
            bz      r4, copybytes2  % Copying is finished
            lb      r5, 0, r1       % Copy the byte
            sb      0, r2, r5
            subi    r3, r3, 1       % Update r1, r2, r3
            addi    r1, r1, 1
            addi    r2, r2, 1
            j       copybytes1
copybytes2  jr      r15
