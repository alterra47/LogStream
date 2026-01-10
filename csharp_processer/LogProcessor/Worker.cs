using NetMQ;
using NetMQ.Sockets;
using Newtonsoft.Json;
using System.Diagnostics;

namespace LogProcessor;

public class Worker : BackgroundService
{
    private readonly ILogger<Worker> _logger;
    private const int BatchSize = 100;
    private static readonly TimeSpan FlushInterval = TimeSpan.FromMilliseconds(500);

    public Worker(ILogger<Worker> logger)
    {
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("C# Log Processor Service starting (Batch Mode)...");

        using (var subscriber = new SubscriberSocket())
        {
            subscriber.Options.ReceiveHighWatermark = 100000;
            subscriber.Connect("tcp://127.0.0.1:5556");
            subscriber.Subscribe("");

            var logBuffer = new List<LogEntry>();
            var timer = Stopwatch.StartNew();

            while (!stoppingToken.IsCancellationRequested)
            {
                // Try to receive. wait up to 10ms for a message (prevents CPU spike)
                if (subscriber.TryReceiveFrameString(out var messageJson))
                {
                    try 
                    {
                        var logData = JsonConvert.DeserializeObject<LogEntry>(messageJson);
                        if (logData != null) logBuffer.Add(logData);
                    }
                    catch (Exception ex) 
                    {
                        _logger.LogError($"JSON Error: {ex.Message}");
                    }
                }
                else 
                {
                    // No message received, small delay to be polite to CPU
                    await Task.Delay(1);
                }

                // Check Flush Condition
                bool timeIsUp = timer.Elapsed >= FlushInterval;
                bool bufferIsFull = logBuffer.Count >= BatchSize;

                if ((timeIsUp || bufferIsFull) && logBuffer.Count > 0)
                {
                    await FlushLogsToDb(logBuffer);
                    logBuffer.Clear();
                    timer.Restart();
                }
            }
        }
    }

    private async Task FlushLogsToDb(List<LogEntry> logs)
    {
        try 
        {
            using (var db = new LogDbContext())
            {
                db.Logs.AddRange(logs);
                await db.SaveChangesAsync();
                _logger.LogInformation($"[Batch] Saved {logs.Count} logs. (ID Range: {logs[0].Id} - {logs[logs.Count-1].Id})");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError($"[DB Error] {ex.Message}");
        }
    }
}