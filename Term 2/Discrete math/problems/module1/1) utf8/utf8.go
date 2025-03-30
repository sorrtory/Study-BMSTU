package main

import (
	"fmt"
)

func encode(utf32 []rune) []byte {
	var out []byte
	const (
		RuneError = '\uFFFD'     // the "error" Rune or "Unicode replacement character"
		RuneSelf  = 0x80         // characters below RuneSelf are represented as themselves in a single byte.
		MaxRune   = '\U0010FFFF' // Maximum valid Unicode code point.
		UTFMax    = 4            // maximum number of bytes of a UTF-8 encoded Unicode character.
	)

	// Code points in the surrogate range are not valid for UTF-8.
	const (
		surrogateMin = 0xD800
		surrogateMax = 0xDFFF
	)

	const (
		t1 = 0b00000000
		tx = 0b10000000
		t2 = 0b11000000
		t3 = 0b11100000
		t4 = 0b11110000
		t5 = 0b11111000

		maskx = 0b00111111
		mask2 = 0b00011111
		mask3 = 0b00001111
		mask4 = 0b00000111

		rune1Max = 1<<7 - 1
		rune2Max = 1<<11 - 1
		rune3Max = 1<<16 - 1

		// The default lowest and highest continuation byte.
		locb = 0b10000000
		hicb = 0b10111111

		// These names of these constants are chosen to give nice alignment in the
		// table below. The first nibble is an index into acceptRanges or F for
		// special one-byte cases. The second nibble is the Rune length or the
		// Status for the special one-byte case.
		xx = 0xF1 // invalid: size 1
		as = 0xF0 // ASCII: size 1
		s1 = 0x02 // accept 0, size 2
		s2 = 0x13 // accept 1, size 3
		s3 = 0x03 // accept 0, size 3
		s4 = 0x23 // accept 2, size 3
		s5 = 0x34 // accept 3, size 4
		s6 = 0x04 // accept 0, size 4
		s7 = 0x44 // accept 4, size 4
	)

	for _, r := range utf32 {
		p := make([]byte, 4)
		// Negative values are erroneous. Making it unsigned addresses the problem.
		switch i := uint32(r); {
		case i <= rune1Max:
			p[0] = byte(r)
			out = append(out, p[:1]...)
		case i <= rune2Max:
			_ = p[1] // eliminate bounds checks
			p[0] = t2 | byte(r>>6)
			p[1] = tx | byte(r)&maskx
			out = append(out, p[:2]...)
		case i > MaxRune, surrogateMin <= i && i <= surrogateMax:
			r = RuneError
			fallthrough
		case i <= rune3Max:
			_ = p[2] // eliminate bounds checks
			p[0] = t3 | byte(r>>12)
			p[1] = tx | byte(r>>6)&maskx
			p[2] = tx | byte(r)&maskx
			out = append(out, p[:3]...)
		default:
			_ = p[3] // eliminate bounds checks
			p[0] = t4 | byte(r>>18)
			p[1] = tx | byte(r>>12)&maskx
			p[2] = tx | byte(r>>6)&maskx
			p[3] = tx | byte(r)&maskx
			out = append(out, p[:4]...)
		}
	}
	return out
}

func decode(utf8 []byte) []rune {
	var out []rune
	const (
		RuneError = '\uFFFD'     // the "error" Rune or "Unicode replacement character"
		RuneSelf  = 0x80         // characters below RuneSelf are represented as themselves in a single byte.
		MaxRune   = '\U0010FFFF' // Maximum valid Unicode code point.
		UTFMax    = 4            // maximum number of bytes of a UTF-8 encoded Unicode character.
	)

	// Code points in the surrogate range are not valid for UTF-8.
	const (
		surrogateMin = 0xD800
		surrogateMax = 0xDFFF
	)

	const (
		t1 = 0b00000000
		tx = 0b10000000
		t2 = 0b11000000
		t3 = 0b11100000
		t4 = 0b11110000
		t5 = 0b11111000

		maskx = 0b00111111
		mask2 = 0b00011111
		mask3 = 0b00001111
		mask4 = 0b00000111

		rune1Max = 1<<7 - 1
		rune2Max = 1<<11 - 1
		rune3Max = 1<<16 - 1

		// The default lowest and highest continuation byte.
		locb = 0b10000000
		hicb = 0b10111111

		// These names of these constants are chosen to give nice alignment in the
		// table below. The first nibble is an index into acceptRanges or F for
		// special one-byte cases. The second nibble is the Rune length or the
		// Status for the special one-byte case.
		xx = 0xF1 // invalid: size 1
		as = 0xF0 // ASCII: size 1
		s1 = 0x02 // accept 0, size 2
		s2 = 0x13 // accept 1, size 3
		s3 = 0x03 // accept 0, size 3
		s4 = 0x23 // accept 2, size 3
		s5 = 0x34 // accept 3, size 4
		s6 = 0x04 // accept 0, size 4
		s7 = 0x44 // accept 4, size 4
	)

	// first is information about the first byte in a UTF-8 sequence.
	var first = [256]uint8{
		//   1   2   3   4   5   6   7   8   9   A   B   C   D   E   F
		as, as, as, as, as, as, as, as, as, as, as, as, as, as, as, as, // 0x00-0x0F
		as, as, as, as, as, as, as, as, as, as, as, as, as, as, as, as, // 0x10-0x1F
		as, as, as, as, as, as, as, as, as, as, as, as, as, as, as, as, // 0x20-0x2F
		as, as, as, as, as, as, as, as, as, as, as, as, as, as, as, as, // 0x30-0x3F
		as, as, as, as, as, as, as, as, as, as, as, as, as, as, as, as, // 0x40-0x4F
		as, as, as, as, as, as, as, as, as, as, as, as, as, as, as, as, // 0x50-0x5F
		as, as, as, as, as, as, as, as, as, as, as, as, as, as, as, as, // 0x60-0x6F
		as, as, as, as, as, as, as, as, as, as, as, as, as, as, as, as, // 0x70-0x7F
		//   1   2   3   4   5   6   7   8   9   A   B   C   D   E   F
		xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, // 0x80-0x8F
		xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, // 0x90-0x9F
		xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, // 0xA0-0xAF
		xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, // 0xB0-0xBF
		xx, xx, s1, s1, s1, s1, s1, s1, s1, s1, s1, s1, s1, s1, s1, s1, // 0xC0-0xCF
		s1, s1, s1, s1, s1, s1, s1, s1, s1, s1, s1, s1, s1, s1, s1, s1, // 0xD0-0xDF
		s2, s3, s3, s3, s3, s3, s3, s3, s3, s3, s3, s3, s3, s4, s3, s3, // 0xE0-0xEF
		s5, s6, s6, s6, s7, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, xx, // 0xF0-0xFF
	}
	// acceptRange gives the range of valid values for the second byte in a UTF-8
	// sequence.
	type acceptRange struct {
		lo uint8 // lowest value for second byte.
		hi uint8 // highest value for second byte.
	}

	// acceptRanges has size 16 to avoid bounds checks in the code that uses it.
	var acceptRanges = [16]acceptRange{
		0: {locb, hicb},
		1: {0xA0, hicb},
		2: {locb, 0x9F},
		3: {0x90, hicb},
		4: {locb, 0x8F},
	}

	p := make([]byte, len(utf8))
	copy(p, utf8)

	for len(p) != 0 {
		n := len(p)
		if n < 1 {
			out = append(out, RuneError)
			break

		}
		p0 := p[0]
		x := first[p0]
		if x >= as {
			// The following code simulates an additional check for x == xx and
			// handling the ASCII and invalid cases accordingly. This mask-and-or
			// approach prevents an additional branch.
			mask := rune(x) << 31 >> 31 // Create 0x0000 or 0xFFFF.
			out = append(out, rune(p[0])&^mask|RuneError&mask)
			p = p[1:]
			continue
		}
		sz := int(x & 7)
		accept := acceptRanges[x>>4]
		if n < sz {
			out = append(out, RuneError)
			p = p[1:]
			break
		}
		b1 := p[1]
		if b1 < accept.lo || accept.hi < b1 {
			out = append(out, RuneError)
			p = p[1:]
			break
		}
		if sz <= 2 { // <= instead of == to help the compiler eliminate some bounds checks
			out = append(out, rune(p0&mask2)<<6|rune(b1&maskx))
			p = p[2:]
			continue
		}
		b2 := p[2]
		if b2 < locb || hicb < b2 {
			out = append(out, RuneError)
			p = p[1:]
			break

		}
		if sz <= 3 {
			out = append(out, rune(p0&mask3)<<12|rune(b1&maskx)<<6|rune(b2&maskx))
			p = p[3:]
			continue
		}
		b3 := p[3]
		if b3 < locb || hicb < b3 {
			out = append(out, RuneError)
			p = p[1:]
			break
		}
		out = append(out, rune(p0&mask4)<<18|rune(b1&maskx)<<12|rune(b2&maskx)<<6|rune(b3&maskx))
		p = p[4:]

	}
	return out

}

func main() {
	utf32 := []rune{0x1F602, 0x0041, 0x2264, 0x1F602}

	fmt.Println(encode(utf32))
	fmt.Println(decode(encode(utf32)))

}
