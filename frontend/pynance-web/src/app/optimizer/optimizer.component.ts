import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-optimizer',
  templateUrl: './optimizer.component.html'
})
export class OptimizerComponent implements OnInit {

  private mockAllocations: number[] = []
  private optimizeDisabled : boolean = false;
  private clearDisabled : boolean = true;
  private calculated : boolean = false;

  @Input() private explanationDisabled;

  constructor() { }


  ngOnInit() {
  }

  public optimize(){
    this.calculated = true;
    this.optimizeDisabled = true;
    this.clearDisabled = false;
  }

  public clear(){
    this.calculated = false;
    this.optimizeDisabled = false;
    this.clearDisabled = true;
  }

  public getAllocations(): number[]{
    if (this.calculated){ return [0.2, 0.2, 0.2, 0.2, 0.2] }
    else{ return [] }
  }
}
