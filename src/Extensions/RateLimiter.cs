using Bonsai;
using System;
using System.ComponentModel;
using System.Linq;
using System.Reactive.Linq;
using System.Threading.Tasks;
using System.Xml.Serialization;
using System.Xml;

[Combinator]
[Description("Limits the maximum rate at which notifications are sent by queueing any intermediate fast notifications.")]
[WorkflowElementCategory(ElementCategory.Combinator)]
public class RateLimiter
{
    [XmlIgnore]
    [Description("The minimum delay between each message sent through the limiter.")]
    public TimeSpan MessageDelay { get; set; }

    [Browsable(false)]
    [XmlElement("MessageDelay")]
    public string MessageDelayXml
    {
        get { return XmlConvert.ToString(MessageDelay); }
        set { MessageDelay = XmlConvert.ToTimeSpan(value); }
    }

    public IObservable<TSource> Process<TSource>(IObservable<TSource> source)
    {
        return source.Select(value => Observable.FromAsync(async cancellationToken =>
        {
            await Task.Delay(MessageDelay, cancellationToken);
            return value;
        })).Concat();
    }
}
