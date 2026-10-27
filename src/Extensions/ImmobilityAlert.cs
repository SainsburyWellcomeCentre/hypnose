using Bonsai;
using OpenCV.Net;
using System;
using System.ComponentModel;
using System.Diagnostics;
using System.Net;
using System.Reactive.Linq;
using System.Text;
using System.Threading.Tasks;

public enum AlertService
{
    Slack,
    Teams
}

[Combinator]
[Description("Tracks how long the mouse centroid has stayed within Radius pixels. Outputs the minutes stationary, and sends a Slack/Teams message when that exceeds AlertAfterMinutes.")]
[WorkflowElementCategory(ElementCategory.Transform)]
public class ImmobilityAlert
{
    float radius = 15f;
    [Category("Detection")]
    [Description("Jitter tolerance in pixels. Centroid movements smaller than this are ignored.")]
    public float Radius
    {
        get { return radius; }
        set { radius = value; }
    }

    double alertAfterMinutes = 90;
    [Category("Detection")]
    [Description("Send an alert once the mouse has been stationary for this many minutes.")]
    public double AlertAfterMinutes
    {
        get { return alertAfterMinutes; }
        set { alertAfterMinutes = value; }
    }

    AlertService service = AlertService.Slack;
    [Category("Notification")]
    [Description("Slack or Teams (Workflows) webhook.")]
    public AlertService Service
    {
        get { return service; }
        set { service = value; }
    }

    [Category("Notification")]
    [Description("The incoming webhook URL. Leave empty to use WebhookUrlFile instead.")]
    public string WebhookUrl { get; set; }

    [Category("Notification")]
    [Description("Optional: path to a text file containing only the webhook URL (keeps the URL out of the .bonsai file / Git). Used when WebhookUrl is empty. Relative paths are relative to the workflow folder.")]
    [Editor("Bonsai.Design.OpenFileNameEditor, Bonsai.Design", "System.Drawing.Design.UITypeEditor, System.Drawing, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a")]
    public string WebhookUrlFile { get; set; }

    string rigName = "Hypnose NP Rig";
    [Category("Notification")]
    [Description("Name used in the message so the researcher knows which rig/mouse it is.")]
    public string RigName
    {
        get { return rigName; }
        set { rigName = value; }
    }

    bool notifyWhenMovingAgain = true;
    [Category("Notification")]
    [Description("Also send a message when the mouse starts moving again after an alert.")]
    public bool NotifyWhenMovingAgain
    {
        get { return notifyWhenMovingAgain; }
        set { notifyWhenMovingAgain = value; }
    }

    bool sendTestOnStart = true;
    [Category("Notification")]
    [Description("Send a test message when the workflow starts, to check the webhook works.")]
    public bool SendTestOnStart
    {
        get { return sendTestOnStart; }
        set { sendTestOnStart = value; }
    }

    public IObservable<double> Process(IObservable<Point2f> source)
    {
        return Observable.Defer(() =>
        {
            var anchor = new Point2f(float.NaN, float.NaN);
            var timer = Stopwatch.StartNew();
            var alerted = false;
            var url = ResolveUrl();

            if (SendTestOnStart)
            {
                Notify(url, string.Format("[{0}] Rig Start: immobility monitor started at {1:HH:mm}.", RigName, DateTime.Now));
            }

            return source.Select(p =>
            {
                // Only update when the mouse is actually detected (Centroid gives NaN otherwise)
                if (!float.IsNaN(p.X) && !float.IsNaN(p.Y))
                {
                    var dx = p.X - anchor.X;
                    var dy = p.Y - anchor.Y;
                    if (float.IsNaN(anchor.X) || dx * dx + dy * dy > Radius * Radius)
                    {
                        // Mouse moved beyond the jitter radius: re-anchor and restart the clock
                        anchor = p;
                        timer.Restart();

                        if (alerted)
                        {
                            alerted = false;
                            if (NotifyWhenMovingAgain)
                            {
                                Notify(url, string.Format("[{0}] Mouse is moving again ({1:HH:mm}).", RigName, DateTime.Now));
                            }
                        }
                    }
                }

                var minutes = timer.Elapsed.TotalMinutes;
                if (!alerted && minutes >= AlertAfterMinutes)
                {
                    alerted = true;
                    Notify(url, string.Format(
                        "<!channel> [{0}] ALERT: mouse has not moved for {1:F0} minutes (since {2:HH:mm}). Please check on it.",
                        RigName, minutes, DateTime.Now - timer.Elapsed));
                }

                return minutes;
            });
        });
    }

    string ResolveUrl()
    {
        if (!string.IsNullOrWhiteSpace(WebhookUrl)) return WebhookUrl.Trim();
        if (string.IsNullOrWhiteSpace(WebhookUrlFile)) return null;
        try
        {
            return System.IO.File.ReadAllText(WebhookUrlFile).Trim();
        }
        catch (Exception ex)
        {
            Trace.WriteLine("ImmobilityAlert could not read WebhookUrlFile: " + ex.Message);
            return null;
        }
    }

    void Notify(string url, string text)
    {
        var service = Service;
        // Send in the background so the camera pipeline never waits on the network
        Task.Run(() => Post(url, service, text));
    }

    static void Post(string url, AlertService service, string text)
    {
        if (string.IsNullOrWhiteSpace(url))
        {
            Trace.WriteLine("ImmobilityAlert (no webhook set): " + text);
            return;
        }

        try
        {
            ServicePointManager.SecurityProtocol |= SecurityProtocolType.Tls12;
            var escaped = text.Replace("\\", "\\\\").Replace("\"", "\\\"");
            string json;
            if (service == AlertService.Slack)
            {
                json = "{\"text\":\"" + escaped + "\"}";
            }
            else
            {
                json = "{\"type\":\"message\",\"attachments\":[{\"contentType\":\"application/vnd.microsoft.card.adaptive\"," +
                       "\"content\":{\"$schema\":\"http://adaptivecards.io/schemas/adaptive-card.json\",\"type\":\"AdaptiveCard\"," +
                       "\"version\":\"1.2\",\"body\":[{\"type\":\"TextBlock\",\"wrap\":true,\"text\":\"" + escaped + "\"}]}}]}";
            }

            using (var client = new WebClient())
            {
                client.Encoding = Encoding.UTF8;
                client.Headers[HttpRequestHeader.ContentType] = "application/json";
                client.UploadString(url, "POST", json);
            }
        }
        catch (Exception ex)
        {
            Trace.WriteLine("ImmobilityAlert failed to send message: " + ex.Message);
        }
    }
}
