import { Component, Input, OnInit, ViewChild } from '@angular/core';
import { MatTable } from '@angular/material/table';
import { Holding } from 'src/app/models/holding';
import { LogService } from 'src/app/services/log.service';
import { PynanceService } from 'src/app/services/pynance.service';
import { containsObject, uniqueArray } from 'src/utilities';

@Component({
  selector: 'app-valuation',
  templateUrl: './valuation.component.html'
})
export class ValuationComponent implements OnInit {
  private location : string = "app.widgets.valuation.ValuationComponent"
  public holding : Holding = null;
  public calculateDisabled : boolean = false;
  public clearDisabled : boolean = true; 
  public loaded : boolean = false;
  public loading : boolean = false;
  public displayedColumns : string[] = [];
  public startDate : string = null;
  public endDate : string = null;
  public img: any = null

  @Input()
  public explanationDisabled : boolean = true;

  @ViewChild('statisticsTable')
  private statisticsTable : MatTable<Holding[]>;
  
  constructor(private logs : LogService, 
              private pynance : PynanceService) { }

  ngOnInit(): void {
  }

  public calculate(){

  }

  public clear() : void {
    this.calculateDisabled = true;
    this.clearDisabled = true;
    this.loaded = false;
    this.loading = false;
    this.holding = null;
    this.displayedColumns = [];
    this.statisticsTable.renderRows()
    this.img = null;
  }

  public getTickers() : string{
    return this.holding.ticker
  }

  public setTickers(inputTickers : string[]){
    if (!this.holding){
      this.logs.log(`received tickers: ${inputTickers}`, this.location)
      this.holding ={ ticker: inputTickers[0], allocation: null,
                        shares: null, annual_return: null,
                        annual_volatility: null, sharpe_ratio: null,
                        asset_beta: null, discount_dividend: null
      };
      this.calculateDisabled = false;
      this.clearDisabled = false;
    }
    else{
      this.logs.log(`Received input tickers, but unable to add to full list`, this.location)
    }
  }

  public removeHolding() : void{
    this.holding = null
  }
}
