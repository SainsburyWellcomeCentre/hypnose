using Bonsai;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Reactive.Linq;
using OpenCV.Net;
using DataSchema;

[Combinator]
[Description("Converts a list of DataSchema.Point2d to an array of OpenCV.Net.Point arrays (contours).")]
[WorkflowElementCategory(ElementCategory.Transform)]
public class ConvertPoints
{
    public IObservable<OpenCV.Net.Point[][]> Process(IObservable<List<DataSchema.Point2d>> source)
    {
        return source.Select(PointsList =>
            new OpenCV.Net.Point[][]
            {
                PointsList.Select(Point => new OpenCV.Net.Point((int)Math.Round(Point.X), (int)Math.Round(Point.Y))).ToArray()
            }
        );
    }
}
