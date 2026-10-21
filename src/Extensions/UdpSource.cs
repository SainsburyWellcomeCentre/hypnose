using Bonsai;
using System;
using System.ComponentModel;
using System.Globalization;
using System.Net;
using System.Net.Sockets;
using System.Reactive.Linq;
using System.Text;

[Description("Receives Sirenia/Pinnacle UDP multicast packets. Set StreamName to receive a single stream, or leave it empty to receive all streams.")]
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

    [Description("Optional. Only emit packets whose full stream ID (e.g. 'Mouse1_EEG1') matches this, case-insensitive. Empty = all streams.")]
    public string StreamName { get; set; }

    public override IObservable<SireniaDatagram> Generate()
    {
        return Observable.Using(
            () => CreateClient(),
            client =>
            {
                var filter = string.IsNullOrWhiteSpace(StreamName) ? null : StreamName.Trim();
                return Observable.FromAsync(client.ReceiveAsync)
                    .Repeat()
                    .SelectMany(result =>
                    {
                        SireniaDatagram datagram;
                        if (TryParseDatagram(result.Buffer, out datagram) &&
                            (filter == null || string.Equals(datagram.StreamName, filter, StringComparison.OrdinalIgnoreCase)))
                        {
                            return Observable.Return(datagram);
                        }
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

        var split = streamId.IndexOf('_');
        datagram.StreamName = streamId;
        datagram.DeviceName = split > 0 ? streamId.Substring(0, split) : streamId;
        datagram.ChannelName = split > 0 ? streamId.Substring(split + 1) : streamId;
        datagram.Seconds = seconds;
        datagram.SubSeconds = subSeconds;
        datagram.Value = value;
        return true;
    }
}

public struct SireniaDatagram
{
    public string StreamName { get; set; }   // full ID, e.g. "Mouse1_EEG1"
    public string DeviceName { get; set; }   // part before the first '_'
    public string ChannelName { get; set; }  // part after the first '_'

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
