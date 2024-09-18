# flowpilot

# Actor时间编程模型
# LiteFlow是一个轻量且强大的国产规则引擎框架，可用于复杂的组件化业务的编排领域，独有的DSL规则驱动整个复杂业务，并可实现平滑刷新热部署，支持多种脚本语言规则的嵌入。帮助系统变得更加丝滑且灵活。

https://www.cnblogs.com/u-n-owen/p/16425358.html#%E6%80%9D%E8%80%83%E6%97%A2%E7%84%B6alevelscriptactor%E4%B9%9F%E7%BB%A7%E6%89%BF%E4%BA%8Eaactor%E4%B8%BA%E4%BD%95%E5%85%B3%E5%8D%A1%E8%93%9D%E5%9B%BE%E4%B8%8D%E8%AE%BE%E8%AE%A1%E8%83%BD%E6%B7%BB%E5%8A%A0component

行为树（Behavior Trees）
行为树是一种强大的 AI 系统工具，适用于创建复杂的任务序列。行为树允许你定义一系列任务及其执行条件，使 Actor 能够按照预定义的逻辑执行任务。

行为树基础示例
AI Controller：创建一个自定义 AI 控制器类来控制 Actor 的行为。
Behavior Tree：创建一个行为树资产，并在其中定义任务和条件。
Blackboard：创建一个黑板资产，用于存储行为树中的数据。
// MyAIController.h
#pragma once

#include "CoreMinimal.h"
#include "AIController.h"
#include "MyAIController.generated.h"

UCLASS()
class MYGAME_API AMyAIController : public AAIController
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

protected:
    UPROPERTY(EditDefaultsOnly, Category = "AI")
    UBehaviorTree* BehaviorTree;
};

// MyAIController.cpp
#include "MyAIController.h"
#include "BehaviorTree/BlackboardComponent.h"
#include "BehaviorTree/BehaviorTreeComponent.h"

void AMyAIController::BeginPlay()
{
    Super::BeginPlay();

    if (BehaviorTree)
    {
        RunBehaviorTree(BehaviorTree);
    }
}