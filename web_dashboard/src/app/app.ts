import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { LogApiService, LogEntry } from './services/log-api';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule], // Clean imports
  templateUrl: './app.html',
  styleUrls: ['./app.scss']
})
export class App {
  searchTerm: string = '';
  logs: LogEntry[] = [];

  constructor(private api: LogApiService) {}

  onSearch() {
    if (!this.searchTerm) return;
    this.api.searchLogs(this.searchTerm).subscribe({
      next: (data) => this.logs = data.results,
      error: (err) => console.error(err)
    });
  }

  generateFakeLog() {
    const services = ['auth-service', 'payment-api', 'db-worker'];
    const levels = ['INFO', 'WARN', 'ERROR'];
    const msgs = ['Connection timeout', 'User logged in', 'Payment declined', 'Null pointer exception'];
    
    const s = services[Math.floor(Math.random() * services.length)];
    const l = levels[Math.floor(Math.random() * levels.length)];
    const m = msgs[Math.floor(Math.random() * msgs.length)];

    this.api.ingestLog(s, l, m).subscribe(() => alert('Log Sent!'));
  }
}