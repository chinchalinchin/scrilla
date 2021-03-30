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

  public optimizeDisabled : boolean = true;
  public clearDisabled : boolean = true;
  public optimizeSharpe : boolean = false;
  public optimizedPortfolio : Portfolio = null;
  public loading : boolean = false;
  public tickers: string[] = [];

  @Input() 
  public explanationDisabled;

  @ViewChild(PortfolioComponent)
  public portfolioComponent : PortfolioComponent;
  @ViewChild(ArgumentsComponent)
  public argsComponent : ArgumentsComponent;

  constructor(private logs: LogService,
              private pynance: PynanceService) { }


  ngOnInit() {  }

  ngOnChanges(changes: SimpleChanges){ }

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
      this.loading = true;
      this.pynance.optimize(tickers, end, start, target, invest, this.optimizeSharpe)
                    .subscribe((resPortfolio: Portfolio)=>{ 
                      this.optimizedPortfolio = resPortfolio; 
                      this.portfolioComponent.setOverallReturn(this.optimizedPortfolio.portfolio_return);
                      this.portfolioComponent.setOverallVolatility(this.optimizedPortfolio.portfolio_volatility);
                      this.loading = false;
                    })
    }

  }

  public clear(){
    this.calculated = false;
    this.optimizeDisabled = false;
    this.clearDisabled = true;
    this.optimizedPortfolio = null;
    this.portfolioComponent.setPortfolioAllocations([])
    this.portfolioComponent.setPortfolioShares([])
    this.portfolioComponent.setPortfolioReturns([])
    this.portfolioComponent.setPortfolioVolatilities([])
    this.portfolioComponent.setOverallReturn(null);
    this.portfolioComponent.setOverallVolatility(null);
  }

  public setOptimizeMethod(method : string){
    // if method is sharpe ratio maximization, switch off optimization method
    let currentMethod : boolean = this.optimizeSharpe;
    if(method == OPTIMIZATION_METHODS[1].value){
      this.logs.log(`Switching to Sharpe Ratio maximization`, this.location);
      this.optimizeSharpe = true;
    }
    // otherwise default to optimizing variance
    else{
      this.logs.log(`Switching to Portfolio Variance minimization`, this.location)
      this.optimizeSharpe = false;
    }
    // if already calculated and method is changed
    if (this.calculated && currentMethod != this.optimizeSharpe){
      this.optimizeDisabled = false;
      // TODO: possibly clear portfolio allocations? 
    }
  }

  public setTickers(theseTickers: string[]) : void{ this.tickers = theseTickers; }

  public getTickers(): string[] { return this.tickers; }
  
  public getAllocations() : number[]{
    let allocations : number[] = [];
    // check for existence of portfolioComponent since this method gets 
    // invoked before portfolioComponent is initialized. NOTE: this method
    // is inputted into the portfolioComponent HTML template.
    if (this.portfolioComponent && this.calculated && this.optimizedPortfolio){ 
      for(let holding of Object.entries(this.optimizedPortfolio.holdings)){
        allocations.push(holding[1].allocation);
      }
    }
    return allocations;
  }

  public getReturns() : number[]{
    let returns : number[] = [];
    // check for existence of portfolioComponent since this method gets 
    // invoked before portfolioComponent is initialized. NOTE: this method
    // is inputted into the portfolioComponent HTML template.
    if(this.portfolioComponent && this.calculated && this.optimizedPortfolio){
      for(let holding of Object.entries(this.optimizedPortfolio.holdings)){
        returns.push(holding[1].annual_return)
      }
    }
    return returns;
  }

  public getVolatilities() : number[]{
    let volatilities : number[] = [];
    // check for existence of portfolioComponent since this method gets 
    // invoked before portfolioComponent is initialized. NOTE: this method
    // is inputted into the portfolioComponent HTML template.
    if(this.portfolioComponent && this.calculated && this.optimizedPortfolio){
      for(let holding of Object.entries(this.optimizedPortfolio.holdings)){
        volatilities.push(holding[1].annual_volatility)
      }
    }
    return volatilities;
  }

  public getShares() : number[]{
    let shares: number [] = [];
    // check for existence of portfolioComponent since this method gets 
    // invoked before portfolioComponent is initialized. NOTE: this method
    // is inputted into the portfolioComponent HTML template.
    if(this.portfolioComponent && this.calculated && this.optimizedPortfolio){
      if(this.portfolioComponent.getInvestment()){
        for(let holding of Object.entries(this.optimizedPortfolio.holdings)){
          shares.push(holding[1].shares)
        } 
      }
    }
    return shares;
  }
}
