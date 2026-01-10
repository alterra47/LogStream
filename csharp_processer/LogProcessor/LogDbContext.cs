using Microsoft.EntityFrameworkCore;
using System.ComponentModel.DataAnnotations.Schema;

namespace LogProcessor;

// 1. The Data Model (Matches your SQL Table)
[Table("Logs")] 
public class LogEntry
{
    [Column("Id")]
    public long Id { get; set; }

    [Column("Timestamp")]
    public string Timestamp { get; set; }

    [Column("Service")]
    public string Service { get; set; }

    [Column("Level")]
    public string Level { get; set; }

    [Column("Message")]
    public string Message { get; set; }
}

// 2. The Database Context (Handles the connection)
public class LogDbContext : DbContext
{
    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        // REPLACE 'password' WITH YOUR ACTUAL POSTGRES PASSWORD
        optionsBuilder.UseNpgsql("Host=localhost;Database=logstream_db;Username=postgres;Password=password");
    }

    public DbSet<LogEntry> Logs { get; set; }
}