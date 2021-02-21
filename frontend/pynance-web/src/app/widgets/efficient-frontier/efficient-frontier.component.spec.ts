import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EfficientFrontierComponent } from './efficient-frontier.component';

describe('EfficientFrontierComponent', () => {
  let component: EfficientFrontierComponent;
  let fixture: ComponentFixture<EfficientFrontierComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EfficientFrontierComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(EfficientFrontierComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
