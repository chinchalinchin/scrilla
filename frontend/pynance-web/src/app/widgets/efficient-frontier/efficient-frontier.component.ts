import { THIS_EXPR } from '@angular/compiler/src/output/output_ast';
import { ChangeDetectorRef, Component, Input, OnInit, SimpleChanges, ViewChild, ViewChildren } from '@angular/core';
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
              private pynance: PynanceService,
              private cd: ChangeDetectorRef) { }

  ngOnInit(): void { }

  public calculate(): void{
    this.loading = true
    this.frontierDisabled = true;
    this.clearDisabled = false;

    this.pynance.efficientFrontier(this.tickers, this.startDate, this.endDate, this.investment)
                  .subscribe( (frontier_result)=> {
                      this.frontier=frontier_result;
                      this.cd.detectChanges();
                  });
  }

  ngOnChanges(changes: SimpleChanges){ 
    if(changes.portfolioChildren){
      console.log(changes.portfolioChildren.currentValue.length)
    }
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
    this.tickers = inputTickers;
    this.frontierDisabled=false;
  }

  public getTickers(): string[]{ return this.tickers; }

  public setDates(inputDates : string[]) : void{
    this.startDate = inputDates[0];
    this.endDate = inputDates[1];
  }

  public setInvestment(inputInvest : number): void{
    this.investment = inputInvest;
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
