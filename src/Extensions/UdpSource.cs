using Bonsai;
using System;
using System.ComponentModel;
using System.Collections.Generic;
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
                .Select(result =>
                {
                    var packet = result.Buffer;
                    var datagram = new SireniaDatagram();
                    datagram.StreamName = Encoding.ASCII.GetString(packet, 0, 25).TrimStart();

                    var data = Encoding.ASCII.GetString(packet, 26, packet.Length - 27);
                    var fields = data.Split(',');
                    if (fields.Length != 3) throw new InvalidOperationException("Corrupt datagram received.");

                    datagram.Seconds =int.Parse(fields[0]);
                    datagram.SubSeconds = float.Parse(fields[1]);
                    datagram.Value = float.Parse(fields[2]);
                    return datagram;
                });
            }
        );
    }
}

public struct SireniaDatagram
{
    public string StreamName { get; set; }

    public int Seconds { get; set; }
    public float SubSeconds {get; set;}

    public float Value { get; set; }
}
