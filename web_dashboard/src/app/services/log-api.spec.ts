import { TestBed } from '@angular/core/testing';

import { LogApi } from './log-api';

describe('LogApi', () => {
  let service: LogApi;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(LogApi);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
