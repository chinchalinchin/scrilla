import { Component, Input, OnInit, ViewChild } from '@angular/core';
import { ArgumentsComponent } from '../args/arguments.component';
import { PortfolioComponent } from '../portfolio/portfolio.component';

@Component({
  selector: 'app-optimizer',
  templateUrl: './optimizer.component.html'
})
export class OptimizerComponent implements OnInit {

  public optimizeDisabled : boolean = false;
  public clearDisabled : boolean = true;
  
  @Input() public explanationDisabled;

  @ViewChild(PortfolioComponent)
  public portfolio : PortfolioComponent;

  @ViewChild(ArgumentsComponent)
  public arguments : ArgumentsComponent;

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
