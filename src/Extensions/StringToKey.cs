using Bonsai;
using System;
using System.ComponentModel;
using System.Linq;
using System.Reactive.Linq;
using System.Windows.Forms;

[Combinator]
[Description("Converts a string to a Keys value.")]
[WorkflowElementCategory(ElementCategory.Transform)]
public class StringToKey
{
    public IObservable<Keys> Process(IObservable<string> source)
    {
        return source.Select(value => {
            var k = new KeysConverter();
            return (Keys)k.ConvertFromString(value);
        });
    }
}