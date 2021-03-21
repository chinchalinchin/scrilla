import { THIS_EXPR } from '@angular/compiler/src/output/output_ast';
import { Component, Input, OnInit, SimpleChanges, ViewChild } from '@angular/core';
import { Portfolio } from 'src/app/models/portfolio';
import { LogService } from 'src/app/services/log.service';
import { PynanceService } from 'src/app/services/pynance.service';
import { ArgumentsComponent, OPTIMIZATION_METHODS } from '../../input/args/arguments.component';
import { PortfolioComponent } from '../../input/portfolio/portfolio.component';

@Component({
  selector: 'app-optimizer',
  templateUrl: './optimizer.component.html'
})
export class OptimizerComponent implements OnInit {
  private location : string = "app.widgets.optimizer.OptimizerComponent";
  private calculated : boolean = false; 

  public optimizeDisabled : boolean = false;
  public clearDisabled : boolean = true;
  public optimizeVariance : boolean = true;
  public optimizedPortfolio : Portfolio = null;

  @Input() 
  public explanationDisabled;

  @ViewChild(PortfolioComponent)
  public portfolioComponent : PortfolioComponent;
  @ViewChild(ArgumentsComponent)
  public argsComponent : ArgumentsComponent;

  constructor(private logs: LogService,
              private pynance: PynanceService) { }


  ngOnInit() {
    this.optimizeDisabled = true;
  }

  ngOnChanges(changes: SimpleChanges){

  }

  public optimize(){
    this.calculated = true;
    this.optimizeDisabled = true;
    this.clearDisabled = false;
    /**
     * TODO: check if tickers on portfolio have been set.
     *       check if target return has been set.
     *       check if optimization method has been set
     *       check if dates have been set
     *       create service to query backend
     *       pass (tickers, dates, target return)
     *       store allocations somewhere
     * 
     *       if conditions for query haven't been met,
     *        print invalidation messages (component specific messages?) 
     */
    let tickers = this.portfolioComponent.getTickers();
    if (tickers){
      let start = this.portfolioComponent.getStartDate()
      let end = this.portfolioComponent.getEndDate();
      let target = this.portfolioComponent.getTargetReturn();
      let invest = this.portfolioComponent.getInvestment();
      this.pynance.optimize(tickers, end, start,target,invest,this.optimizeVariance)
                    .subscribe((resPortfolio: Portfolio)=>{
                      this.optimizedPortfolio = resPortfolio;
                      console.log(this.optimizedPortfolio)
                      Object.keys(this.optimizedPortfolio).forEach((prop)=> console.log(prop));
                    })
    }
  }

  public clear(){
    this.calculated = false;
    this.optimizeDisabled = true;
    this.clearDisabled = true;
    // TODO: clear allocations in portfolio. call setAllocations and pass in null array.
  }

  public setOptimizeMethod(method : string){
    // if method is sharpe ratio maximization, switch off optimization method
    if(method == OPTIMIZATION_METHODS[1].value){
      this.logs.log(`Switching to Sharpe Ratio maximization`, this.location);
      this.optimizeVariance = false;
    }
    // otherwise default to optimizing variance
    else{
      this.logs.log(`Switching to Portfolio Variance minimization`, this.location)
      this.optimizeVariance = true;
    }
  }

  public getAllocations(): number[]{
    let allocations : number[] = []
    if (this.calculated && this.optimizedPortfolio){ 
      for(let holding of this.optimizedPortfolio.holdings){
        allocations.push(holding.allocation);
      }
    }
    return allocations;
  }
}
