import { MatTable } from '@angular/material/table';
import { Component, EventEmitter, Input, OnInit, Output, SimpleChanges, ViewChild } from '@angular/core';
import { Holding } from 'src/app/models/holding';
import { containsObject, arraysEqual, uniqueArray } from 'src/utilities';
import { LogService } from 'src/app/services/log.service';

@Component({
  selector: 'app-portfolio',
  templateUrl: './portfolio.component.html'
})
/**PortfolioComponent
 *  This component receives ticker symbols inputted by the user in the child ArgumentsComponent
 *    and gets loaded by its parent component, whether that be OptimizerComponent or 
 *    EfficientFrontierComponent, with the percentage of the portfolio that should be dedicated
 *    to each asset in the user ticker symbol list. 
 * 
 * Input:
 *  This component requires two number arrays as an argument,
 * 
 *        <app-portfolio [allocations]="[0,0.5,0.25,0.25]"
 *                        [shares] = "[0,2,1,1]"></app-portfolio>
 * 
 *  'allocations' must be an ordered array of portfolio allocations corresponding to the 
 *    the tickers inputted into the ArgumentsComponent and passed into this component
 *    from its parent component. In other words, if the user specifies the ticker list of 
 *    ["ALLY", "BX", "SNE"], then the allocation array of, say, [0.25, 0.3, 0.45] would represent 
 *    an 25% ALLY allocation, a 30% BX allocation and a 45% SNE allocation.
 * 
 *  'shares' must be an ordered array of portfolio shares corresponding to the tickers inputted 
 *    into the ArgumentsComponent and passed into this component from its parent component. In
 *    other words, if the user specifies the ticker list of ["ALLY", "BX", "SNE"], then the shares
 *    array of, say, [1, 2, 3] would represent 1 ALLY share, 2 BX shares and 3 SNE shares.
 * 
 * Output:
 *  This component emits a clear event signalling the user has cleared all ticker symbols
 *    from the portfolio. To hook into the event,
 * 
 *        <app-portfolio [allocations] = "[array]" (clearEvent) = "doSomething()"></app-portfolio>
 * 
 * 
 */
export class PortfolioComponent implements OnInit {
  private location : string = "app.input.portfolio.PortfolioComponent"

  public portfolio: Holding[] = [];
  public clearDisabled : boolean = true;
  public displayedColumns: string[] = [];
  public startDate: string = null;
  public endDate: string = null;
  public targetReturn: number = null;
  public investment: number = null;
  public overallReturn : number = null;
  public overallVolatility : number = null;

  @ViewChild('portfolioTable')
  private portfolioTable : MatTable<Holding[]>;

  @Input()
  private allocations: number[]
  @Input()
  private shares: number[];
  @Input()
  private returns: number[];
  @Input()
  private volatilities: number[];

  @Output()
  private clearEvent = new EventEmitter<boolean>();

  constructor(private logs: LogService){ }

  ngOnInit() { } 
  
  ngOnChanges(changes: SimpleChanges) {    
    if (changes.allocations) {
      if(!arraysEqual(changes.allocations.currentValue, changes.allocations.previousValue)){
        if(this.portfolio.length != 0){
          // empty portfolio passed in
          if(changes.allocations.currentValue.length == 0){ 
            for(let holding of this.portfolio){ holding.allocation = null; }
            this.displayedColumns = [ 'ticker' ]
          }
          // allocation portfolio passed in
          else{
            if (changes.allocations.currentValue.length == this.portfolio.length){
              this.setPortfolioAllocations(changes.allocations.currentValue)
              this.displayedColumns = [ 'ticker', 'allocation' ]
            }
            else{
              let logMessage = `Portfolio length ${this.portfolio.length} does not equal `
                                + `new allocation length ${changes.allocations.currentValue.length}`
              this.logs.log(logMessage, this.location)
            }
          } 
        }
      }
    }

    if(changes.shares){
      if(!arraysEqual(changes.shares.currentValue, changes.shares.previousValue)){
        if(this.portfolio.length != 0){
          // empty portfolio passed in
          if(changes.shares.currentValue.length == 0){
            for(let holding of this.portfolio) { holding.shares= null; }
            this.displayedColumns = ['ticker'];
          }
          // shares portfolio passed in
          else{
            if(changes.shares.currentValue.length == this.portfolio.length){
              this.setPortfolioShares(changes.shares.currentValue);
              this.displayedColumns = [ 'ticker', 'allocation', 'shares'];
            }
            else{
              let logMessage = `Portfolio length ${this.portfolio.length} does not equal `
                                + `new shares length ${changes.shares.currentValue.length}`;
              this.logs.log(logMessage, this.location);
            }
          }
        }
      }
    }

    if(changes.returns){
      if(!arraysEqual(changes.returns.currentValue, changes.returns.previousValue)){
        if(this.portfolio.length != 0){
          //empty portfolio passed in
          if(changes.returns.currentValue.length == 0){
            for(let holding of this.portfolio) { holding.annual_return = null; }
            this.displayedColumns = ['ticker']
          }
          else{
            if(changes.returns.currentValue.length == this.portfolio.length){
              this.setPortfolioReturns(changes.returns.currentValue);
              if(this.investment){
                this.displayedColumns = [ 'ticker', 'allocation', 'shares', 'return']
              }
              else{
                this.displayedColumns = [ 'ticker', 'allocation', 'return']
              }
            }
            else{
              let logMessage = `Portfolio length ${this.portfolio.length} does not equal `
                                + `new returns length ${changes.returns.currentValue.length}`;
              this.logs.log(logMessage, this.location);
            }
          }
        }
      }
    }

    if(changes.volatilities){
      if(!arraysEqual(changes.volatilities.currentValue, changes.volatilities.previousValue)){
        if(this.portfolio.length != 0){
          //empty portfolio passed in
          if(changes.volatilities.currentValue.length == 0){
            for(let holding of this.portfolio) { holding.annual_volatility = null; }
            this.displayedColumns = ['ticker']
          }
        
          else{
            if(changes.volatilities.currentValue.length == this.portfolio.length){
              this.setPortfolioVolatilities(changes.volatilities.currentValue);
              if(this.investment){
                this.displayedColumns = [ 'ticker', 'allocation', 'shares', 'return', 'volatility']
              }
              else{
                this.displayedColumns = [ 'ticker', 'allocation', 'return', 'volatility']
              }
            }
            else{
              let logMessage = `Portfolio length ${this.portfolio.length} does not equal `
                                + `new returns length ${changes.volatilities.currentValue.length}`;
              this.logs.log(logMessage, this.location);
            }
          }
        }
      }
    }

  }

  public getTickers() : string[]{
    let tickers : string [] = []
    for(let holding of this.portfolio){
      tickers.push(holding.ticker)
    }
    return tickers;
  }
  
  public removeHolding(holding : Holding) : void{
    let index = this.portfolio.indexOf(holding);
    this.portfolio.splice(index, 1);

    this.setPortfolioAllocations([]);
    if(this.displayedColumns.includes('allocation')){
      index = this.displayedColumns.indexOf('allocation')
      this.displayedColumns.splice(index,1);
    }

    this.setPortfolioShares([]);
    if(this.displayedColumns.includes('shares')){
      index = this.displayedColumns.indexOf('shares');
      this.displayedColumns.splice(index, 1)
    }

    if(this.portfolio.length==0){
      this.clearDisabled=true;
      this.displayedColumns = [];
    }
    this.portfolioTable.renderRows()
  }

  public setTickers(inputTickers: string[]) : void{
    this.logs.log(`received tickers: ${inputTickers}`, this.location)

    let unduplicatedTickers : string[] = [];
    let portfolioTickers : string[] = this.getTickers();
    let filteredInput : string [] = uniqueArray(inputTickers);

    // TODO: use array filtering to do this
    for(let ticker of filteredInput){
      if(!containsObject(ticker, portfolioTickers)){ unduplicatedTickers.push(ticker); }
    }

    for(let ticker of unduplicatedTickers){
      this.portfolio.push({ ticker: ticker, allocation: null, shares: null, 
                            annual_return: null, annual_volatility: null,
                            sharpe_ratio: null, asset_beta: null,
                            discount_dividend: null})
    }
  
    if(this.portfolio.length != 0){
      this.clearDisabled = false;
      this.displayedColumns = [ 'ticker' ]
    }
    
    this.portfolioTable.renderRows()

  }
  
  public setDates(inputDates: string[]) : void {
    this.logs.log(`Received dates ${inputDates}`, this.location)
    this.startDate = inputDates[0]
    // TODO: this looks wrong
    this.endDate = inputDates[1]
  }

  public getStartDate() : string { return this.startDate; }

  public getEndDate() : string { return this.endDate; }

  public setOverallReturn(portfolioReturn : number) : void{ this.overallReturn = portfolioReturn; }

  public getOverallReturn() : number { return this.overallReturn; }

  public setOverallVolatility(portfolioVolatility : number) : void { this.overallVolatility = portfolioVolatility; }

  public getOverallVolatility () : number { return this.overallVolatility; }

  public setPortfolioAllocations(theseAllocations : number[]) : void{
    this.logs.log('Passing allocations to portfolio', this.location);
    let index = 0;
    for(let allocation of theseAllocations){
      let logMessage =`Changing ${this.portfolio[index].ticker} allocation from `
                        + `${this.portfolio[index].allocation} to ${allocation}`;
      this.logs.log(logMessage, this.location);
      this.portfolio[index].allocation = allocation;
      index++;
    }
  }

  public getPortfolioAllocations() : number[]{
    let portfolioAllocations: number[] = [];
    for(let holding of this.portfolio){ portfolioAllocations.push(holding.allocation); }
    return portfolioAllocations;
  }

  public setPortfolioShares(theseShares : number[]): void{
    this.logs.log('Passing shares to portfolio', this.location);
    let index = 0;
    for(let shares of theseShares){
      let logMessage = `Changing ${this.portfolio[index].ticker} shares from `
                        + `${this.portfolio[index].shares} to ${shares}`;
      this.logs.log(logMessage, this.location);
      this.portfolio[index].shares = shares
      index++;
    }
  }

  public getPortfolioShares() : number[]{
    let portfolioShares: number[] = [];
    for(let holding of this.portfolio){ portfolioShares.push(holding.shares); }
    return portfolioShares;
  }

  public setPortfolioReturns(theseRates : number[]) : void{
    this.logs.log('Passing rates of return to portfolio', this.location);
    let index = 0;
    for(let rate of theseRates){
      let logMessage = `Changing ${this.portfolio[index].ticker} rate from `
                        + `${this.portfolio[index].annual_return} to ${rate}`;
      this.logs.log(logMessage, this.location);
      this.portfolio[index].annual_return = rate;
      index++;
    }
  }

  public getPortfolioReturns() : number[]{
    let portfolioReturns : number[] = [];
    for(let holding of this.portfolio) { portfolioReturns.push(holding.annual_return); }
    return portfolioReturns;
  }

  public setPortfolioVolatilities(theseVolatilities : number[]) : void{
    this.logs.log('Passing volatilities to portfolio', this.location);
    let index = 0;
    for(let volatility of theseVolatilities){
      let logMessage = `Changing ${this.portfolio[index].ticker} rate from `
                        + `${this.portfolio[index].annual_volatility} to ${volatility}`;
      this.logs.log(logMessage, this.location);
      this.portfolio[index].annual_volatility = volatility;
      index++;
    }
  }

  public getPortfolioVolatilities() : number[]{
    let portfolioVolatilities : number[] = [];
    for(let holding of this.portfolio) { portfolioVolatilities.push(holding.annual_volatility);}
    return portfolioVolatilities;
  }

  public setTargetReturn(inputTarget : number) : void{
    this.logs.log(`Received target return: ${inputTarget}`, this.location)
    this.targetReturn = inputTarget;
  }

  public getTargetReturn() : number{ return this.targetReturn; }

  public getInvestment() : number { return this.investment; }

  public setInvestment(inputInvestment : number) : void{
    this.logs.log(`Received investment : ${inputInvestment}`, this.location);
    this.investment = inputInvestment;
  }

  public clearPortfolio() : void{
    this.logs.log('Clearing portfolio and table', this.location)
    this.portfolio = [];
    this.clearDisabled = true;
    this.displayedColumns = [];
    this.clearEvent.emit(true);
  }

}
