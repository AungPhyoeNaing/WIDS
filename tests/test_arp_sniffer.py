import unittest
from unittest.mock import MagicMock
from ids.arp_sniffer import ARPSniffer

# Create a mock ARP packet class since scapy might not be available or 
# we don't want to rely on the actual packet in tests
class MockARP:
    def __init__(self, op, psrc, hwsrc, hwdst):
        self.op = op
        self.psrc = psrc
        self.hwsrc = hwsrc
        self.hwdst = hwdst

class MockPacket:
    def __init__(self, arp_layer=None):
        self._arp_layer = arp_layer

    def haslayer(self, layer):
        return self._arp_layer is not None
        
    def __getitem__(self, layer):
        return self._arp_layer

class TestARPSniffer(unittest.TestCase):
    def setUp(self):
        self.mock_callback = MagicMock()
        self.sniffer = ARPSniffer(self.mock_callback)

    def test_normal_arp_reply_no_alert(self):
        packet = MockPacket(MockARP(op=2, psrc="192.168.1.1", hwsrc="AA:AA:AA:AA:AA:AA", hwdst="BB:BB:BB:BB:BB:BB"))
        self.sniffer._handle_packet(packet)
        self.mock_callback.assert_not_called()
        self.assertEqual(self.sniffer.arp_table["192.168.1.1"], "AA:AA:AA:AA:AA:AA")

    def test_arp_spoof_detection(self):
        # First ARP reply (normal)
        packet1 = MockPacket(MockARP(op=2, psrc="192.168.1.1", hwsrc="AA:AA:AA:AA:AA:AA", hwdst="BB:BB:BB:BB:BB:BB"))
        self.sniffer._handle_packet(packet1)
        
        # Second ARP reply from SAME IP but DIFFERENT MAC (Spoofing)
        packet2 = MockPacket(MockARP(op=2, psrc="192.168.1.1", hwsrc="CC:CC:CC:CC:CC:CC", hwdst="BB:BB:BB:BB:BB:BB"))
        self.sniffer._handle_packet(packet2)
        
        # Check if callback was called with spoofed alert
        self.assertTrue(self.mock_callback.called)
        alert = self.mock_callback.call_args[0][0]
        self.assertEqual(alert["type"], "ARP")
        self.assertEqual(alert["subtype"], "ARP Spoof")
        self.assertTrue(alert["spoofed"])
        self.assertEqual(alert["source_ip"], "192.168.1.1")
        self.assertEqual(alert["old_mac"], "AA:AA:AA:AA:AA:AA")
        self.assertEqual(alert["mac_src"], "CC:CC:CC:CC:CC:CC")

if __name__ == "__main__":
    unittest.main()
