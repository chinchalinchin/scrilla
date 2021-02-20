// Angular Core Imports
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

// Custom Component Imports
import { AppComponent } from './app.component';
import { OptimizerComponent } from './optimizer/optimizer.component';
import { TickerComponent } from './ticker/ticker.component';
import { PortfolioComponent } from './portfolio/portfolio.component';

// Angular Material Imports
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';



@NgModule({
  declarations: [
    AppComponent,
    OptimizerComponent,
    TickerComponent,
    PortfolioComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    MatCardModule,
    MatIconModule,
    MatListModule,
    MatButtonModule,
    MatInputModule,
    MatTableModule,
    MatFormFieldModule,
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
