import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { OptimizerComponent } from './optimizer.component';

describe('OptimizerComponent', () => {
  let component: OptimizerComponent;
  let fixture: ComponentFixture<OptimizerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ OptimizerComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(OptimizerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
