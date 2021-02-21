import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-optimizer',
  templateUrl: './optimizer.component.html'
})
export class OptimizerComponent implements OnInit {

  public optimizeDisabled : boolean = false;
  public clearDisabled : boolean = true;
  
  @Input() public explanationDisabled;

  private mockAllocations: number[] = []
  private calculated : boolean = false; 

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
