import { Component, Input, OnInit, ViewChild, ViewChildren } from '@angular/core';
import { ArgumentsComponent } from 'src/app/input/args/arguments.component';
import { PortfolioComponent } from 'src/app/input/portfolio/portfolio.component';
import { Portfolio } from 'src/app/models/portfolio';
import { LogService } from 'src/app/services/log.service';
import { PynanceService } from 'src/app/services/pynance.service';
import { containsObject, uniqueArray } from 'src/utilities';

@Component({
  selector: 'app-efficient-frontier',
  templateUrl: './efficient-frontier.component.html'
})
export class EfficientFrontierComponent implements OnInit {
  private location : string = "app.widgets.efficient=frontier.EfficientFrontierComponent";

  public loading : boolean = false;
  public loaded : boolean = false;
  public frontier : Portfolio[] = [];
  public frontierDisabled : boolean = true;
  public clearDisabled : boolean = true;
  public img : any = null;

  public tickers : string[] = []
  public investment : number = null;
  public startDate : string = null;
  public endDate : string = null;

  @Input()
  public explanationDisabled : boolean = true;

  @ViewChildren(PortfolioComponent)
  public portfolioChildren : PortfolioComponent[];
  @ViewChild(ArgumentsComponent)
  public args : ArgumentsComponent;
  
  constructor(private logs: LogService,
              private pynance: PynanceService) { }

  ngOnInit(): void { }

  public calculate(): void{
    this.loading = true
    this.frontierDisabled = true;
    this.clearDisabled = false;

    this.pynance.efficientFrontier(this.tickers, this.startDate, this.endDate, this.investment)
                  .subscribe( (frontier_result)=> {
                      this.frontier=frontier_result;
                      // todo: propagate overall return and volatilities down through children
                  });
    
  }


  public clear(): void{
    this.loading = false;
    this.loaded = false;
    this.frontier = [];
    this.tickers = [];
    this.startDate = null;
    this.endDate = null;
    this.investment = null;
    this.clearDisabled = true;
    this.frontierDisabled = true;
    this.img = null;
  }
  
  public setTickers(inputTickers : string[]) : void{
    let unduplicatedTickers : string[] = [];
    let filteredInput : string [] = uniqueArray(inputTickers);

    // TODO: use array filtering to do this
    for(let ticker of filteredInput){
      if(!containsObject(ticker, this.tickers)){ unduplicatedTickers.push(ticker); }
    }
    this.tickers = unduplicatedTickers;
    this.frontierDisabled=false;
  }

  public setDates(inputDates : string[]) : void{
    this.startDate = inputDates[0];
    this.endDate = inputDates[1];
  }

  public setInvestment(inputInvest : number): void{
    this.investment = inputInvest;
  }

  public propagateFrontiers(): void{
    for(let child of this.portfolioChildren){
      let index = this.portfolioChildren.indexOf(child);
      // TODO: pass frontier to portfolioChildren
      //    tickers: 
      //    shares:
      //    allocations:
      //    returns:
      //    volatilities:
      //    overall_return
      //    overall_volatility
      this.frontier[index]
    }
  }

  public getAllocations(thisPortfolio: Portfolio) : number[]{
    let allocations : number[] = [];
    for(let holding of Object.entries(thisPortfolio.holdings)){
      allocations.push(holding[1].allocation);
    }
    return allocations
  }

  public getReturns(thisPortfolio: Portfolio) : number[]{
    let returns : number[] = [];
    for(let holding of Object.entries(thisPortfolio.holdings)){
      returns.push(holding[1].annual_return);
    }
    return returns;
  }

  public getVolatilities(thisPortfolio: Portfolio) : number[]{
    let volatilities : number[] = [];
    for(let holding of Object.entries(thisPortfolio.holdings)){
      volatilities.push(holding[1].annual_volatility);
    }
    return volatilities;
  }

  public getShares(thisPortfolio: Portfolio) : number[]{
    let shares : number[] = [];
    for(let holding of Object.entries(thisPortfolio.holdings)){
      shares.push(holding[1].shares);
    }
    return shares;
  }

}
