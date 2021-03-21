import { MatTable } from '@angular/material/table';
import { Component, EventEmitter, Input, OnInit, Output, SimpleChanges, ViewChild } from '@angular/core';
import { Holding } from 'src/app/models/holding';
import { containsObject } from 'src/utilities';
import { mockPortfolio } from 'src/app/models/holding'
import { LogService } from 'src/app/services/log.service';

@Component({
  selector: 'app-portfolio',
  templateUrl: './portfolio.component.html'
})
/**PortfolioComponent
 * This component receives ticker symbols inputted by the user in the child ArgumentsComponent
 *  and gets loaded by its parent component, whether that be OptimizerComponent or 
 *  EfficientFrontierComponent, with the percentage of the portfolio that should be dedicated
 *  to each asset in the user ticker symbol list. 
 * 
 * Input:
 * This component requires a number array as an argument,
 * 
 * <app-portfolio [allocations]="[0,0.5,0.25,0.25]"></app-portfolio>
 * 
 * 'allocations' must be an ordered array of portfolio allocations corresponding to the 
 *  the tickers passed in through the ArgumentsComponent child. In other words, if the user
 *  specifies the ticker list of ["ALLY", "BX", "SNE"], then the allocation array of, say,
 *  [0.25, 0.3, 0.45] would represent an 25% ALLY allocation, a 30% BX allocation and a 45%
 *  SNE allocation.
 * 
 * 
 */
export class PortfolioComponent implements OnInit {
  public portfolio: Holding[] = [];
  public clearDisabled : boolean = true;
  public displayedColumns: string[] = [];
  public startDate: string;
  public endDate: string;
  public targetReturn: number;
  private location : string = "app.input.PortfolioComponent"

  @ViewChild('portfolioTable')
  private portfolioTable : MatTable<Holding[]>;

  @Input()
  private allocations: number[]

  @Output()
  private clearEvent = new EventEmitter<boolean>();

  constructor(private logs: LogService){ }

  ngOnInit() { } 
  
  ngOnChanges(changes: SimpleChanges) {    
    if (changes.allocations) {

      if(changes.allocations.currentValue != changes.allocations.previousValue){
        if(this.portfolio.length != 0){
          // empty portfolio passed in
          if(changes.allocations.currentValue.length == 0){ 
            for(let holding of this.portfolio){ holding.allocation = null; }
            this.displayedColumns = [ 'ticker' ]
          }

          // allocation portfolio passed in
          else{
            // check if allocations.length = portfolio.length
            if (changes.allocations.currentValue == this.portfolio.length){
              let index = 0;
              for(let newAllocation of changes.allocations.currentValue){
                let logMessage =`Changing ${this.portfolio[index].ticker} allocation from `
                                  + `${this.portfolio[index].allocation} to ${newAllocation}`
                this.logs.log(logMessage, this.location)
                this.portfolio[index].allocation = newAllocation
                index++;
              }
              this.displayedColumns = [ 'ticker', 'allocation']
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

  }

  public getTickers(): string[]{
    let tickers : string [] = []
    for(let holding of this.portfolio){
      tickers.push(holding.ticker)
    }
    return tickers;
  }

  public setTickers(inputTickers: string[]) : void{
    this.logs.log(`received inputTickers: ${inputTickers}`, this.location)

    let unduplicatedTickers : string[] = [];
    let portfolioTickers : string[] = this.getTickers();
    
    for(let ticker of inputTickers){
      if(!containsObject(ticker, portfolioTickers)){ unduplicatedTickers.push(ticker); }
    }

    for(let ticker of unduplicatedTickers){
      this.portfolio.push({ ticker: ticker, allocation: null, return: null, volatility: null})
    }
  
    if(this.portfolio.length != 0){
      this.clearDisabled = false;
      this.displayedColumns = [ 'ticker' ]
    }
    
    this.portfolioTable.renderRows()

  }
  
  public setDates(inputDates: string[]) : void {
    this.logs.log(`received inputDates ${inputDates}`, this.location)
    this.startDate = inputDates[0]
    this.endDate = inputDates[0]
  }

  public getStartDate(): string { return this.startDate; }

  public getEndDate(): string { return this.endDate; }

  public setAllocations(theseAllocations : number[]) : void{
    this.logs.log('Passing allocations to portfolio', this.location)
    for(let portion of theseAllocations){
      let thisIndex : number = theseAllocations.indexOf(portion)
      this.portfolio[thisIndex].allocation = portion
    }
  }

  public getAllocations(): number[]{
    return this.allocations;
  }

  public getPortfolioAllocations(): number[]{
    let portfolioAllocations: number[] = [];
    for(let holding of this.portfolio){ portfolioAllocations.push(holding.allocation); }
    return portfolioAllocations;
  }

  public setTargetReturn(inputTarget : number){
    this.logs.log(`Received inputTarget: ${inputTarget}`, this.location)
    this.targetReturn = inputTarget;
  }

  public getTargetReturn(): number{ return this.targetReturn; }

  public clearPortfolio() : void{
    this.logs.log('Clearing portfolio and table', this.location)
    this.portfolio = [];
    this.clearDisabled = true;
    this.displayedColumns = [];
    this.clearEvent.emit(true);
  }

}
