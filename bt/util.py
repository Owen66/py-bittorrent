import hashlib
import struct

class DownloadCompleteException(Exception):
    pass

def sha1_hash(string):
    """Return 20-byte sha1 hash of string.
    """
    return hashlib.sha1(string).digest()

class Bitfield(object):
    def __init__(self, bool_array, total_length):
        """Return at least len(bool_array) bits as complete bytes.

           Bit at position i represents client's posession (1)
            or lack (0) of the data at bool_array[i].

        """
        assert len(bool_array) == total_length
        str_output = ""
        for b in bool_array:
            str_output += "1" if b else "0"
        difference = total_length - len(str_output)
        while len(str_output) % 8 != 0:
            str_output += "0"
        #print 'len(str_output) was', len(str_output)
        byte_array = ""
        for i in range(0, len(str_output), 8):
            # Convert string of 1's and 0's to base 2 integer
            # print 'adding', repr(struct.pack('>B', int(str_output[i:i+8], 2)))
            byte_array += \
                    struct.pack('>B', int(str_output[i:i+8], 2))
        """
        print type(byte_array)
        print 'byte array len was', len(byte_array)
        bits = ''.join(str(bit) for bit in self._bits(byte_array))
        assert len(byte_array) == self.client.torrent.num_pieces / 8
        """
        self.byte_array = byte_array
    @classmethod
    def _bits(cls, data):
        data_bytes = (ord(b) for b in data)
        for b in data_bytes:
            """Get bit by reducing b by 2^i.
               Bitwise AND outputs 1s and 0s as strings.
            """
            for i in reversed(xrange(8)): # msb on left
                yield (b >> i) & 1
    @classmethod
    def parse(cls, peer, bitfield):
        """Decrease piece rarity for each piece the peer reports it has.
        """
        print 'Received bitfield'
        bitfield_length = len(bitfield)
        bits = ''.join(str(bit) for bit in cls._bits(bitfield))
        # Trim spare bits
        pieces_length = len(peer.client.torrent.pieces)
        try:
            """ Sanity check: do peer & client expect same # of pieces?
                Check extra bits only.
            """
            assert len(filter(lambda b: b=='1', bits[pieces_length:])) == 0
        except AssertionError:
            raise Exception('Peer reporting too many pieces in "bitfield."')

        bits = bits[:pieces_length]
        # Modify torrent state with new information
        for i in range(len(bits)):
            bit = bits[i]
            if bit == '1':
                peer.client.torrent.decrease_rarity(i,peer.peer_id)
