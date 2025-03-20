using Bonsai;
using System;
using System.ComponentModel;
using System.Collections.Generic;
using System.Linq;
using System.Reactive.Linq;
using DataSchema;

[Combinator]
[Description("")]
[WorkflowElementCategory(ElementCategory.Transform)]
public class NullOrUnrewarded
{
    public IObservable<bool> Process(IObservable<Valence> source)
    {
        return source.Select(value => {
            if (value == null) {
                return true;
            }

            return !value.Rewarded;
        });
    }
}
