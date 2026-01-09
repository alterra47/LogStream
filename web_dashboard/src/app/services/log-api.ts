import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface LogEntry {
  _id: number;
  timestamp: string;
  service: string;
  level: string;
  message: string;
}

export interface SearchResponse {
  count: number;
  results: LogEntry[];
}

@Injectable({
  providedIn: 'root'
})
export class LogApiService {
  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) { }

  // Send a new log (for testing via UI)
  ingestLog(service: string, level: string, message: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/ingest`, { service, level, message });
  }

  // Search logs
  searchLogs(term: string): Observable<SearchResponse> {
    return this.http.get<SearchResponse>(`${this.apiUrl}/search?term=${term}`);
  }
}