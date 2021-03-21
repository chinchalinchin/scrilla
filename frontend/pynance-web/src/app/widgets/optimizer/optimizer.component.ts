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
    // TODO: 
  }

  public optimize(){
    this.calculated = true;
    this.optimizeDisabled = true;
    this.clearDisabled = false;
   
    let tickers = this.portfolioComponent.getTickers();
    if (tickers){
      let start = this.portfolioComponent.getStartDate()
      let end = this.portfolioComponent.getEndDate();
      let target = this.portfolioComponent.getTargetReturn();
      let invest = this.portfolioComponent.getInvestment();
      this.pynance.optimize(tickers, end, start,target,invest,this.optimizeVariance)
                    .subscribe((resPortfolio: Portfolio)=>{ this.optimizedPortfolio = resPortfolio; })
    }

  }

  public clear(){
    this.calculated = false;
    this.optimizeDisabled = false;
    this.clearDisabled = true;
  }

  public setOptimizeMethod(method : string){
    // if method is sharpe ratio maximization, switch off optimization method
    let currentMethod : boolean = this.optimizeVariance;
    if(method == OPTIMIZATION_METHODS[1].value){
      this.logs.log(`Switching to Sharpe Ratio maximization`, this.location);
      this.optimizeVariance = false;
    }
    // otherwise default to optimizing variance
    else{
      this.logs.log(`Switching to Portfolio Variance minimization`, this.location)
      this.optimizeVariance = true;
    }
    // if already calculated and method is changed
    if (this.calculated && currentMethod != this.optimizeVariance){
      this.optimizeDisabled = false;
      // TODO: possibly clear portfolio allocations? 
    }
  }

  public getAllocations(): number[]{
    let allocations : number[] = []
    if (this.calculated && this.optimizedPortfolio){ 
      for(let holding of Object.entries(this.optimizedPortfolio.holdings)){
        allocations.push(holding[1].allocation);
      }
    }
    return allocations;
  }

  public getShares(): number[]{
    let shares: number [] = [];
    if(this.portfolioComponent.getInvestment() && this.calculated && this.optimizedPortfolio){
      for(let holding of Object.entries(this.optimizedPortfolio.holdings)){
        shares.push(holding[1].shares)
      }
    }
    return shares;
  }
}
