using Bonsai;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Globalization;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Reactive.Linq;
using System.Text;

[Description("Receives Sirenia/Pinnacle UDP multicast packets. Set DeviceName to receive all streams of that device (e.g. 16514 gives EEG1_16514, EEG2_16514, EMG_16514). Leave it empty to receive everything.")]
public class UdpSource : Source<SireniaDatagram>
{
    const int StreamIdLength = 26;

    public UdpSource()
    {
        GroupAddress = "239.255.76.67";
        Port = 8866;
    }

    [Description("Multicast group address Pinnacle sends to.")]
    public string GroupAddress { get; set; }

    [Description("UDP port Pinnacle sends to.")]
    public int Port { get; set; }

    [Description("Optional IP of the network adapter to join the group on (e.g. 127.0.0.1 if Pinnacle runs on this PC). Empty = OS default.")]
    public string LocalAddress { get; set; }

    [Description("Optional. Device/dongle ID (the part after the last underscore in the packet ID, e.g. 16514). Only streams of this device are emitted. Empty = all devices.")]
    public string DeviceName { get; set; }

    public override IObservable<SireniaDatagram> Generate()
    {
        return Observable.Using(
            () => CreateClient(),
            client =>
            {
                var device = string.IsNullOrWhiteSpace(DeviceName) ? null : DeviceName.Trim();
                return Observable.FromAsync(client.ReceiveAsync)
                    .Repeat()
                    .SelectMany(result =>
                    {
                        SireniaDatagram datagram;
                        if (TryParseDatagram(result.Buffer, out datagram) &&
                            (device == null || string.Equals(datagram.Device.Id, device, StringComparison.OrdinalIgnoreCase)))
                            return Observable.Return(datagram);
                        return Observable.Empty<SireniaDatagram>();
                    });
            });
    }

    UdpClient CreateClient()
    {
        // ReuseAddress must be set BEFORE binding, so several UdpSource nodes
        // (one per stream) can all listen on the same port at once.
        var client = new UdpClient();
        try
        {
            client.Client.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, true);
            client.Client.ReceiveBufferSize = 4 * 1024 * 1024; // avoid drops during bursts
            client.Client.Bind(new IPEndPoint(IPAddress.Any, Port));

            var group = IPAddress.Parse(GroupAddress);
            if (string.IsNullOrWhiteSpace(LocalAddress))
                client.JoinMulticastGroup(group);
            else
                client.JoinMulticastGroup(group, IPAddress.Parse(LocalAddress.Trim()));
            return client;
        }
        catch
        {
            client.Dispose();
            throw;
        }
    }

    static readonly char[] PadChars = { '\0', ' ', '\r', '\n', '\t' };

    static bool TryParseDatagram(byte[] packet, out SireniaDatagram datagram)
    {
        datagram = new SireniaDatagram();
        if (packet == null || packet.Length <= StreamIdLength)
            return false;

        // Header: 26-byte stream ID, padded with nulls/spaces
        var streamId = Encoding.ASCII.GetString(packet, 0, StreamIdLength).Trim(PadChars);

        // Payload: "seconds,subseconds,value" plus optional terminator
        var data = Encoding.ASCII.GetString(packet, StreamIdLength, packet.Length - StreamIdLength).Trim(PadChars);
        var fields = data.Split(',');
        if (fields.Length != 3)
            return false;

        int seconds;
        double subSeconds;
        float value;
        if (!int.TryParse(fields[0].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out seconds) ||
            !double.TryParse(fields[1].Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out subSeconds) ||
            !float.TryParse(fields[2].Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out value))
            return false;

        // Stream ID is "<stream>_<device>", e.g. "EEG1_16514"
        var split = streamId.LastIndexOf('_');
        datagram.StreamName = streamId;
        datagram.ChannelName = split > 0 ? streamId.Substring(0, split) : streamId;
        datagram.Device = split > 0 ? streamId.Substring(split + 1) : string.Empty;
        datagram.Seconds = seconds;
        datagram.SubSeconds = subSeconds;
        datagram.Value = value;
        return true;
    }
}

public struct DeviceId
{
    // CsvWriter drops the last member name of a string column header, so the string sits one level below Device.
    public string Id { get; set; }

    public static implicit operator DeviceId(string id)
    {
        return new DeviceId { Id = id };
    }

    public override string ToString()
    {
        return Id;
    }
}

public struct SireniaDatagram
{
    public string StreamName { get; set; }   // full ID, e.g. "EEG1_16514"
    public DeviceId Device { get; set; }     // part after the last '_', e.g. "16514"
    public string ChannelName { get; set; }  // part before the last '_', e.g. "EEG1"

    public int Seconds { get; set; }
    public double SubSeconds { get; set; }

    // Sender-side sample time. Assumes SubSeconds is a fraction of a second;
    // if it turns out to be milliseconds, use Seconds + SubSeconds / 1000.
    public double Time { get { return Seconds + SubSeconds; } }

    public float Value { get; set; }

    public override string ToString()
    {
        return string.Format(CultureInfo.InvariantCulture, "{0} t={1:F6} v={2}", StreamName, Time, Value);
    }
}
