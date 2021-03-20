import { TestBed } from '@angular/core/testing';

import { PynanceService } from './pynance.service';

describe('PynanceService', () => {
  let service: PynanceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(PynanceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
