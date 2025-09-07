using Bonsai;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Reactive.Linq;
using OpenCV.Net;
using DataSchema;

[Combinator]
[Description("Converts a list of DataSchema.Point2d to an array of OpenCV.Net.Point2f.")]
[WorkflowElementCategory(ElementCategory.Transform)]
public class ConvertPoints
{
    public IObservable<OpenCV.Net.Point2f[]> Process(IObservable<List<DataSchema.Point2d>> source)
    {
        return source.Select(PointsList =>
            PointsList.Select(Point => new OpenCV.Net.Point2f((float)Point.X, (float)Point.Y)).ToArray()
        );
    }
}
