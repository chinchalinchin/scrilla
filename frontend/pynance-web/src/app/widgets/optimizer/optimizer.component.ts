import { Component, Input, OnInit, SimpleChanges, ViewChild } from '@angular/core';
import { ArgumentsComponent } from '../../input/args/arguments.component';
import { PortfolioComponent } from '../../input/portfolio/portfolio.component';

@Component({
  selector: 'app-optimizer',
  templateUrl: './optimizer.component.html'
})
export class OptimizerComponent implements OnInit {

  public optimizeDisabled : boolean = false;
  public clearDisabled : boolean = true;

  private calculated : boolean = false; 

  @Input() 
  public explanationDisabled;

  @ViewChild(PortfolioComponent)
  public portfolio : PortfolioComponent;
  @ViewChild(ArgumentsComponent)
  public arguments : ArgumentsComponent;

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
