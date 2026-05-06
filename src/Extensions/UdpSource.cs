using Bonsai;
using System;
using System.ComponentModel;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reactive.Linq;
using System.Net.Sockets;
using System.Net;
using System.Text;

public class UdpSource : Source<SireniaDatagram>
{
    public string GroupAddress { get; set; }

    public int Port { get; set; }

    public override IObservable<SireniaDatagram> Generate()
    {
        return Observable.Using(
            () => new UdpClient(Port),
            client =>
            {
                var multicastAddress = IPAddress.Parse(GroupAddress);
                client.JoinMulticastGroup(multicastAddress);

                var endPoint = new IPEndPoint(IPAddress.Any, Port);
                return Observable.FromAsync(client.ReceiveAsync)
                .Repeat()
                .SelectMany(result =>
                {
                    var packet = result.Buffer;
                    SireniaDatagram datagram;
                    if (TryParseDatagram(packet, out datagram))
                    {
                        return Observable.Return(datagram);
                    }

                    return Observable.Empty<SireniaDatagram>();
                });
            }
        );
    }

    static bool TryParseDatagram(byte[] packet, out SireniaDatagram datagram)
    {
        datagram = new SireniaDatagram();
        if (packet == null || packet.Length < 27)
        {
            return false;
        }

        var data = Encoding.ASCII.GetString(packet, 26, packet.Length - 27);
        var fields = data.Split(',');
        if (fields.Length != 3)
        {
            return false;
        }

        int seconds;
        float subSeconds;
        float value;
        if (!int.TryParse(fields[0].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out seconds) ||
            !float.TryParse(fields[1].Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out subSeconds) ||
            !float.TryParse(fields[2].Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out value))
        {
            return false;
        }

        datagram.StreamName = Encoding.ASCII.GetString(packet, 0, 25).TrimStart();
        datagram.Seconds = seconds;
        datagram.SubSeconds = subSeconds;
        datagram.Value = value;
        return true;
    }
}

public struct SireniaDatagram
{
    public string StreamName { get; set; }

    public int Seconds { get; set; }
    public float SubSeconds {get; set;}

    public float Value { get; set; }
}
