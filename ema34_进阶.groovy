//+------------------------------------------------------------------+
//|                                                      EMA34EA.mq4 |
//|                                  Enhanced Trailing Stop Version |
//|                                       Updated by ChatGPT         |
//+------------------------------------------------------------------+
#property copyright "ChatGPT"
#property version   "1.02"
#property strict

//--- 输入参数
input int    StopLossPoints = 300;     // 初始止损点数
input int    TakeProfitPoints = 1000;  // 止盈点数
input double RiskPercent = 10.0;       // 风险比例
input int    TrailTrigger = 150;       // 移动止损触发点数（新增）
input int    TrailStop = 100;          // 移动止损点数（新增）

//--- 全局变量
datetime lastConditionTime;

//+------------------------------------------------------------------+
//| 专家初始化函数                                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   lastConditionTime = 0;
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| 核心交易逻辑                                                     |
//+------------------------------------------------------------------+
void OnTick()
{
   CheckEntryConditions();  // 处理入场条件
   TrailingStopManagement();// 新增移动止损管理
}

//+------------------------------------------------------------------+
//| 入场条件检查                                                     |
//+------------------------------------------------------------------+
void CheckEntryConditions()
{
   if(OrdersTotal() > 0) return;
   
   bool initialCondition = CheckInitialCondition();
   if(initialCondition)
   {
      double ema34 = iMA(NULL,0,34,0,MODE_EMA,PRICE_CLOSE,0);
      double currentPrice = Close[0];
      
      if(MathAbs(currentPrice - ema34) <= 1*Point)
      {
         bool priceWasAbove = CheckPriceHistory(ema34, lastConditionTime, true);
         bool priceWasBelow = CheckPriceHistory(ema34, lastConditionTime, false);
         
         if(priceWasAbove) OpenTrade(OP_BUY, ema34);
         if(priceWasBelow) OpenTrade(OP_SELL, ema34);
      }
   }
}

//+------------------------------------------------------------------+
//| 移动止损管理系统（新增关键功能）                                 |
//+------------------------------------------------------------------+
void TrailingStopManagement()
{
   for(int i=OrdersTotal()-1; i>=0; i--)
   {
      if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
      {
         if(OrderSymbol() == Symbol() && OrderComment() == "EMA34 Strategy")
         {
            double currentProfit = 0;
            double newStopLoss = 0;
            
            if(OrderType() == OP_BUY)
            {
               // 计算浮动盈利（以点数为单位）
               currentProfit = (Bid - OrderOpenPrice())/Point;
               // 计算新止损（保本+100点）
               newStopLoss = OrderOpenPrice() + TrailStop*Point;
               
               // 当盈利超过触发值且当前止损不符合新标准
               if(currentProfit >= TrailTrigger && 
                  (OrderStopLoss() < newStopLoss || OrderStopLoss() == 0))
               {
                  OrderModify(OrderTicket(), OrderOpenPrice(),
                             newStopLoss, 
                             OrderTakeProfit(), 0, CLR_NONE);
               }
            }
            
            if(OrderType() == OP_SELL)
            {
               currentProfit = (OrderOpenPrice() - Ask)/Point;
               newStopLoss = OrderOpenPrice() - TrailStop*Point;
               
               if(currentProfit >= TrailTrigger && 
                  (OrderStopLoss() > newStopLoss || OrderStopLoss() == 0))
               {
                  OrderModify(OrderTicket(), OrderOpenPrice(),
                             newStopLoss, 
                             OrderTakeProfit(), 0, CLR_NONE);
               }
            }
         }
      }
   }
}

//（保持原有CheckInitialCondition、CheckPriceHistory、OpenTrade函数不变）