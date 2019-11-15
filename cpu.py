"""CPU functionality."""
import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MULT = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
SP = 3
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.register = [0] * 8
        self.pc = 0

        self.branchtable = {}        
        self.branchtable[HLT] = self.handle_hlt
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[PRN] = self.handle_prn
        self.branchtable[MULT] = self.handle_mult
        self.branchtable[POP] = self.handle_pop
        self.branchtable[PUSH] = self.handle_push
        self.register[SP] = 0xf4
        

        self.halted = False

    def load(self):
        """Load a program into memory."""

        print(sys.argv)
        if len(sys.argv) != 2:
            print("usage: comp.py [filename]")
            sys.exit(1)

        prog = sys.argv[1]
        address = 0


        with open(prog) as f:
            for line in f:
                line = line.split("#")[0]
                line = line.strip()

                if line == "":
                    continue

                val = int(line, 2)
                self.ram[address] = val
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        elif op == "MULT": 
            self.register[reg_a] *= self.register[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def handle_ldi(self):
        reg_num = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        self.register[reg_num] = value

    def handle_prn(self):
        reg_num = self.ram_read(self.pc + 1)
        print(self.register[reg_num])

    def handle_hlt(self):
        self.halted = True

    def handle_mult(self):
        num1 = self.ram_read(self.pc + 1)
        print(f"num1: {num1}")
        num2 = self.ram_read(self.pc + 2)
        print(f"num2: {num2}")
        self.alu("MULT", num1, num2)    

    def handle_pop(self):
        val = self.ram[self.register[SP]]
        reg_num = self.ram_read(self.pc + 1)
        self.register[reg_num] = val
        self.register[SP] += 1

    def handle_push(self):
        self.register[SP] -= 1
        reg_num = self.ram_read(self.pc + 1)
        val = self.register[reg_num]
        self.ram[self.register[SP]] = val



    def run(self):
        """Run the CPU."""
        
        while self.halted != True:
            ir = self.ram[self.pc]
            val = ir
            op_count = val >> 6
            ir_length = op_count + 1
            self.branchtable[ir]()

            if ir == 0 or None:
                print(f"Unknown instructions and index {self.pc}")
                sys.exit(1)

            self.pc += ir_length