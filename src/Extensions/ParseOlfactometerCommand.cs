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
public class ParseOlfactometerCommand
{
    public IObservable<OlfactometerBitMask> Process(IObservable<OlfactometerStateCommand> source)
    {
        return source.Select(value => {
            return new OlfactometerBitMask {
                // Append 0 to ensure non-empty list, aggregate with bitwise OR (in case a valve value is duplicated)
                ValvesO0 = value.ValvesOpenO0.Select(e => (int)Math.Pow(2, e)).Append(0).Aggregate((a, b) => a | b),
                ValvesO1 = value.ValvesOpenO1.Select(e => (int)Math.Pow(2, e)).Append(0).Aggregate((a, b) => a | b),
                EndValvesO0 = value.EndValvesOpenO0.Select(e => (int)Math.Pow(2, e)).Append(0).Aggregate((a, b) => a | b),
                EndValvesO1 = value.EndValvesOpenO1.Select(e => (int)Math.Pow(2, e)).Append(0).Aggregate((a, b) => a | b),
            };
        });
    }
}

public class OlfactometerBitMask {
    public int ValvesO0;
    public int ValvesO1;
    public int EndValvesO0;
    public int EndValvesO1;
}
