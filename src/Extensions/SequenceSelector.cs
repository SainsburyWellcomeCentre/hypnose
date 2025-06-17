using Bonsai;
using System;
using SequenceSchema;
using System.ComponentModel;
using System.Reactive.Linq;
using System.IO;
using YamlDotNet.Core;
using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;

public class SequenceSelector : Source<HypnoseSequence>
{
    private HypnoseSequence Sequence;

    private string path = "";
    [Editor("Bonsai.Design.OpenFileNameEditor, Bonsai.Design", DesignTypes.UITypeEditor)]
    public string Path {
        get {
            return path;
        }
        set {
            path = value;

            HypnoseSequence settings;
            using (var reader = new StreamReader(value)) {
                var parser = new MergingParser(new Parser(reader));

                var deserializer = new DeserializerBuilder()
                    .WithNamingConvention(CamelCaseNamingConvention.Instance)
                    .Build();
                
                settings = deserializer.Deserialize<HypnoseSequence>(parser);
            }

            Console.WriteLine("Changed");
            Sequence = settings;
            OnValueChanged(Sequence);
        }
    }

    event Action<HypnoseSequence> ValueChanged;

    void OnValueChanged(HypnoseSequence value)
    {
        if (ValueChanged != null) {
            ValueChanged.Invoke(value);
        }
    }

    public override IObservable<HypnoseSequence> Generate()
    {
        return Observable
            .Defer(() => Observable.Return(Sequence))
            .Concat(Observable.FromEvent<HypnoseSequence>(
                handler => ValueChanged += handler,
                handler => ValueChanged -= handler));;
    }
}