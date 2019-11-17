"""CPU functionality"""
import sys

HLT = 0b00000001 
LDI = 0b10000010 
PRN = 0b01000111 
MULT = 0b10100010 
POP = 0b01000110 
PUSH = 0b01000101 
CALL = 0b01010000 
RET = 0b00010001 
SP = 244
JMP = 0b01010100 
JEQ = 0b01010101 
JNE = 0b01010110 
CMP = 0b10100111 

class CPU:
    """Main CPU class."""

    def __init__(self, register = [0] * 8, ram = [0] * 256, pc = 0):
        """Construct a new CPU."""
        self.register = register
        self.ram = ram
        self.pc = pc
        self.sp = 244 
        self.running = True

        # Setup Branch Table
        self.branchtable = {}
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[PRN] = self.handle_prn
        self.branchtable[MULT] = self.handle_mult
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[POP] = self.handle_pop
        self.branchtable[HLT] = self.handle_hlt
        self.branchtable[CALL] = self.handle_call
        self.branchtable[RET] = self.handle_ret


        self.branchtable[JMP] = self.handle_jmp
        self.branchtable[JEQ] = self.handle_jeq
        self.branchtable[JNE] = self.handle_jne
        self.branchtable[CMP] = self.handle_cmp

        self.E = 0  
        self.L = 0 
        self.G = 0 

    def load(self):
        """Load a program into memory."""
        program = []

        with open(sys.argv[1]) as f:
            for line in f:
                comment_split = line.split('#')
                num = comment_split[0].strip()
                try:
                    program.append(int(num, 2))
                except ValueError:
                    pass

        address = 0

        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            print("ADDING NOW")
            self.register[reg_a] += self.register[reg_b]
        elif op == "MUL":
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
            print(" %02X" % self.register[i], end='')

        print()

    def ram_read(self, memory_address_register):
        value = self.ram[memory_address_register]
        return value

    def ram_write(self, memory_data_register, memory_address_register):
        self.ram[memory_address_register] = memory_data_register

    def handle_ldi(self):
        reg_num = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        self.register[reg_num] = value

    def handle_prn(self):
        reg_num = self.ram_read(self.pc + 1)
        print(self.register[reg_num])
    
    def handle_hlt(self):
        self.running = False

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


    def handle_call(self):
        next_address = self.pc + 2
        self.sp -= 1
        self.ram[self.sp] = next_address

        address = self.register[self.ram[self.pc + 1]]
        self.pc = address

    def handle_ret(self):
        next_address = self.ram[self.sp]
        self.sp += 1

        self.pc = next_address

    def handle_jmp(self):
        jump_address = self.register[self.ram[self.pc + 1]]
        self.pc = jump_address

    def handle_cmp(self):
        self.E = 0
        self.L = 0
        self.G = 0

        value_one = self.register[self.ram[self.pc + 1]]
        value_two = self.register[self.ram[self.pc + 2]]

        if value_one == value_two:
            self.E = 1
        elif value_one < value_two:
            self.L = 1
        elif value_one > value_two:
            self.G = 1


    def handle_jne(self):
        if self.E == 0:
            self.pc = self.register[self.ram[self.pc + 1]]
        else:
            self.pc += 2

    def handle_jeq(self):
        if self.E == 1:
            self.pc = self.register[self.ram[self.pc + 1]]
        else:
            self.pc += 2

    def run(self):
        """Run the CPU."""
        while self.running:

            ir = self.pc
            op = self.ram[ir]
            instruction_size = ((op & 11000000) >> 6) + 1
            pc_set_flag = (op & 0b00010000) 
            self.branchtable[op]()
            if pc_set_flag != 0b00010000:
                self.pc += instruction_size