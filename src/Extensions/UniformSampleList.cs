using Bonsai;
using System;
using System.ComponentModel;
using System.Collections.Generic;
using System.Linq;
using System.Reactive.Linq;
using SequenceSchema;

[Combinator]
[Description("")]
[WorkflowElementCategory(ElementCategory.Transform)]
public class UniformSampleList
{
    Random random = new Random();

    public IObservable<Sequence> Process(IObservable<List<Sequence>> source)
    {
        return source.Select(x => x[random.Next(x.Count)]);
    }

    public IObservable<Valence> Process(IObservable<List<Valence>> source)
    {
        return source.Select(x => x[random.Next(x.Count)]);
    }
}
