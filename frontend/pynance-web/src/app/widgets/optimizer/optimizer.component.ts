import { THIS_EXPR } from '@angular/compiler/src/output/output_ast';
import { Component, Input, OnInit, SimpleChanges, ViewChild } from '@angular/core';
import { PynanceService } from 'src/app/services/pynance.service';
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
  public portfolioComponent : PortfolioComponent;
  @ViewChild(ArgumentsComponent)
  public argsComponent : ArgumentsComponent;

  constructor(private pynanceService: PynanceService) { }


  ngOnInit() {
  }

  public optimize(){
    this.calculated = true;
    this.optimizeDisabled = true;
    this.clearDisabled = false;
    /**
     * TODO: check if tickers on portfolio have been set.
     *       check if target return has been set.
     *       check if optimization method has been set
     *       create service to query backend
     *       pass (tickers, dates, target return)
     *       store allocations somewhere
     * 
     *       if conditions for query haven't been met,
     *        print invalidation messages (component specific messages?) 
     */
  }

  public clear(){
    this.calculated = false;
    this.optimizeDisabled = false;
    this.clearDisabled = true;
    /**
     * TODO: clear portfolio holding.tickers
     */
  }

  public getAllocations(): number[]{
    if (this.calculated){ return [0.2, 0.2, 0.2, 0.2, 0.2] }
    else{ return [] }
  }
}
