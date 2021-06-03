import sys
import time
import random
import pygame
from pygame import gfxdraw
import bitarray


def main():   
    chip8 = Chip8()
    chip8.load_rom("test_opcode.ch8")

    # pygame parameters
    pygame.init()
    SIZE = width, height = 640, 320
    BLACK = 0, 0, 0
    screen = pygame.display.set_mode(SIZE)
    upscale = pygame.Surface((64, 32))

    # emulator loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        chip8.execute_instruction(screen, upscale)

        time.sleep(0.05)

class Chip8:
    def __init__(self):
        # Initialize ram as empty
        self.ram = []
        empty_byte = 0
        for byte in range(4096):
            self.ram.append(empty_byte)

        # Store sprite data in lower ram (0x000 to 0x1FF)
        fonts = [ 
        0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
        0x20, 0x60, 0x20, 0x20, 0x70, # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
        0x90, 0x90, 0xF0, 0x10, 0x10, # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
        0xF0, 0x10, 0x20, 0x40, 0x40, # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90, # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
        0xF0, 0x80, 0x80, 0x80, 0xF0, # C
        0xE0, 0x90, 0x90, 0x90, 0xE0, # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
        0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]

        # Initialize registers as empty
        self.registers = []
        for reg in range(16):
            self.registers.append(empty_byte)

        self.stack =[]
        self.program_counter = 512
        #self.rom_instructions = [] 
        self.I = 0
        self.carry_flag = 0

    # Open rom file and store bytes(2 bytes at a time) in list
    def load_rom(self, rom_name):
        start_index = 512
        with open(rom_name, "rb") as rom:
            bytes = rom.read(1)
            while bytes != b"":
                self.ram[start_index] = bytes.hex()
                bytes = rom.read(1)
                start_index += 1

    # Decode what instruction we need to do and runs it
    def execute_instruction(self, screen, upscale):
        instruction = self.ram[self.program_counter] + self.ram[self.program_counter + 1]
        vx = self.registers[int(instruction[1], 16)]
        vy = self.registers[int(instruction[2], 16)]
        if instruction[0] == '0':
            if instruction == '00e0':  
                # 00E0 Clears the screen.
                black = 0, 0, 0
                screen.fill(black)
                pygame.display.flip()
            
            elif instruction == '00ee':  
                # 00EE Returns from a subroutine.
                self.program_counter = self.stack.pop()
        
        elif instruction[0] == '1':  
            # 1NNN Jumps to address NNN.
            self.program_counter = int(instruction[1:], 16) - 2
        
        elif instruction[0] == '2':  
            # 2NNN Calls subroutine at NNN.
            self.stack.append(instruction[1:])
        
        elif instruction[0] == '3':  
            # 3XNN Skips the next instruction if VX equals NN. (Usually the next instruction is a jump to skip a code block)
            if vx == int(instruction[2:], 16):
                self.program_counter += 2
        
        elif instruction[0] == '4':  
            # 4XNN Skips the next instruction if VX does not equal NN. (Usually the next instruction is a jump to skip a code block)
            if vx != int(instruction[2:], 16):
                self.program_counter += 2
        
        elif instruction[0] == '5':  
            # 5XY0 Skips the next instruction if VX equals VY. (Usually the next instruction is a jump to skip a code block)
            if vx == vy:
                self.program_counter += 2
        
        elif instruction[0] == '6':  
            # 6XNN Sets VX to NN.
            vx = int(instruction[2:], 16)
            self.registers[int(instruction[1], 16)] = vx
        
        elif instruction[0] == '7':  
            # 7XNN Adds NN to VX. (Carry flag is not changed)
            vx += int(instruction[2:], 16)
            self.registers[int(instruction[1])] = vx
        
        elif instruction[0] == '8':
            if instruction == '8XY0':  
                # 8XY0 Sets VX to the value of VY.
                self.registers[int(instruction[1])] = vy
            
            elif instruction[3] == '1':  
                # 8XY1 Sets VX to VX or VY. (Bitwise OR operation)
                vx |= vy
                self.registers[int(instruction[1])] = vx
            
            elif instruction[3] == '2':  
                # 8XY2 Sets VX to VX and VY. (Bitwise AND operation)
                vx &= vy
                self.registers[int(instruction[1])] = vx
            
            elif instruction[3] == '3':  
                # 8XY3 Sets VX to VX xor VY.
                vx = vx ^ vy
                self.registers[int(instruction[1])] = vx
            
            elif instruction[3] == '4':  
                # 8XY4 Adds VY to VX. VF is set to 1 when there's a carry, and to 0 when there is not.
                vx += vy
                if vx > 255:
                    self.carry_flag = 1
                    vx -= 255
                self.registers[int(instruction[1])] = vx
            
            elif instruction[3] == '5':  
                # 8XY5 VY is subtracted from VX. VF is set to 0 when there's a borrow, and 1 when there is not.
                vx -= vy
                if vx < 0:
                    self.carry_flag = 1
                    vx += 255
                self.registers[int(instruction[1])] = vx
            
            elif instruction[3] == '6':  
                # 8XY6 Stores the least significant bit of VX in VF and then shifts VX to the right by 1
                if vx == 0:
                    self.carry_flag = 0
                else:
                    self.carry_flag = vx & 1
                vx >>= 1
                self.registers[int(instruction[1])] = vx
            
            elif instruction[3] == '7':  
                # 8XY7 Sets VX to VY minus VX. VF is set to 0 when there's a borrow, and 1 when there is not.
                print("8XY7 Sets VX to VY minus VX. VF is set to 0 when there's a borrow, and 1 when there is not.")
            
            elif instruction[3] == 'e':  
                # 8XYe Stores the most significant bit of VX in VF and then shifts VX to the left by 1
                msb = vx << 3
                self.carry_flag = msb
                vx <<= 1
                self.registers[int(instruction[1])] = vx
        
        elif instruction[0] == '9':  
            # 9XY0 Skips the next instruction if VX does not equal VY. (Usually the next instruction is a jump to skip a code block)
            if vx != vy:
                self.program_counter += 2
        
        elif instruction[0] == 'a':  
            # ANNN Sets I to the address NNN.
            self.I = int(instruction[1:], 16)
        
        elif instruction[0] == 'b':  
            # BNNN Jumps to the address NNN plus V0.
            self.program_counter = instruction[1:] + self.registers[0]
        
        elif instruction[0] == 'c':  
            # CXNN Sets VX to the result of a bitwise and operation on a random number (Typically: 0 to 255) and NN.
            vx = instruction[2:] & random.randint(0, 255)
        
        elif instruction[0] == 'd':  
            # DXYN Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N+1 pixels.
            # Go through every byte of a sprite
            for byte in range(int(instruction[3], 16)):
                # Split sprite into bits
                sprite = int(self.ram[self.I + byte], 16)
                sprite_bits = list(bin(sprite))
                while len(sprite_bits) < 10:
                    sprite_bits.insert(2, '0')

                # Bits are XORed into screen
                WHITE = (255, 255, 255)
                BLACK = (0, 0, 0)
                X_OFFSET = 8
                Y_OFFSET = 16
                for x, bit in enumerate(sprite_bits[2:]):
                    bit = int(bit)
                    pixel_on_screen = pygame.Surface.get_at(screen, (vx+x, vy+byte))
                    if bool(pixel_on_screen[0]) ^ bool(bit):
                        gfxdraw.pixel(upscale, vx+x, vy+byte, WHITE)
                        screen.blit(pygame.transform.scale(upscale, (640, 320)), (0,0)) # Upscale to window size
                        pygame.display.update()
                        self.carry_flag = 1
                    else:
                        gfxdraw.pixel(upscale, vx+x, vy+byte, BLACK)
                        screen.blit(pygame.transform.scale(upscale, (640, 320)), (0,0)) # Upscale to window size
                        pygame.display.update()
                        self.carry_flag = 0
        
        elif instruction[0] == 'e':
            if instruction[2:] == '9e':  
                # EX9E Skips the next instruction if the key stored in VX is pressed. (Usually the next instruction is a jump to skip a code block)
                print("EX9E Skips the next instruction if the key stored in VX is pressed. (Usually the next instruction is a jump to skip a code block)")
            
            elif instruction[2:] == 'a1':  
                # EXA1 Skips the next instruction if the key stored in VX is not pressed. (Usually the next instruction is a jump to skip a code block)
                print("EXA1 Skips the next instruction if the key stored in VX is not pressed. (Usually the next instruction is a jump to skip a code block)")
        
        elif instruction[0] == 'f':
            if instruction[2:] == '07':  
                # FX07 Sets VX to the value of the delay timer.
                print("FX07 Sets VX to the value of the delay timer.")
            
            elif instruction[2:] == '0A':  
                # FX0A A key press is awaited, and then stored in VX. (Blocking Operation. All instruction halted until next key event)
                print("FX0A A key press is awaited, and then stored in VX. (Blocking Operation. All instruction halted until next key event)")
            
            elif instruction[2:] == '15': 
                # FX15 Sets the delay timer to VX.
                print("FX15 Sets the delay timer to VX.")
            
            elif instruction[2:] == '18':  
                # FX18 Sets the sound timer to VX.
                print("FX18 Sets the sound timer to VX.")
            
            elif instruction[2:] == '1E':  
                # FX1E Adds VX to I. VF is not affected.
                print("FX1E Adds VX to I. VF is not affected.")
            
            elif instruction[2:] == '29':  
                # FX29 Sets I to the location of the sprite for the character in VX. Characters 0-F (in hexadecimal) are represented by a 4x5 font.
                print("FX29 Sets I to the location of the sprite for the character in VX. Characters 0-F (in hexadecimal) are represented by a 4x5 font.")
                
            
            elif instruction[2:] == '33':  
                # FX33 Stores the binary-coded decimal representation of VX, with the most significant of three digits at the address in I, the middle digit at I plus 1, and the least significant digit at I plus 2. (In other words, take the decimal representation of VX, place the hundreds digit in memory at location in I, the tens digit at location I+1, and the ones digit at location I+2.)
                length = len(str(vx))
                string_vx = str(vx)
                for index in range(length):
                    self.ram[self.I + index] = string_vx[index]
            
            elif instruction[2:] == '55':  
                # FX55 Stores V0 to VX (including VX) in memory starting at address I. The offset from I is increased by 1 for each value written, but I itself is left unmodified.
                for register in range(int(instruction[1], 16)):
                    self.ram[self.I + register] = self.registers[register]
            
            elif instruction[2:] == '65':  
                # FX65 Fills V0 to VX (including VX) with values from memory starting at address I. The offset from I is increased by 1 for each value written, but I itself is left unmodified
                for register in range(int(instruction[1], 16)):
                    self.registers[register] = self.ram[self.I + register]
        else:
            print("Other instruction that didnt get recognized")
        
        self.program_counter += 2

def draw_bigger_pixel(screen, x, y, COLOR):
    rect = (x, y, 8, 16)
    pygame.draw.rect(screen, COLOR, rect)

if __name__ == "__main__":
    main()