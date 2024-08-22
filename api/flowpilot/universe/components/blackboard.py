# 在Unreal Engine（UE）中，Blackboard 是行为树（Behavior Tree）系统的重要组成部分，主要用于存储和管理行为树节点之间共享的数据。Blackboard 提供了一种灵活的机制，使不同的行为树节点能够访问和修改共享的变量，从而实现复杂的AI逻辑和行为。

# ### 主要功能

# 1. **数据存储**：Blackboard 用于存储行为树节点之间共享的变量，这些变量可以是各种类型的，如布尔值、整数、浮点数、向量、对象引用等。
# 2. **数据访问**：行为树中的节点可以读取和写入 Blackboard 中的变量，从而使不同的节点能够共享信息。
# 3. **条件判断**：行为树节点可以根据 Blackboard 中的变量值来决定是否执行某个任务或行为。
# 4. **调试和可视化**：在UE编辑器中，Blackboard 变量可以通过可视化界面进行调试和监控，方便开发和调试AI行为。

# ### 使用示例

# 以下是一个简单的示例，展示如何在 Unreal Engine 中使用 Blackboard 和 Behavior Tree 来实现一个简单的AI逻辑。

# #### 1. 创建Blackboard和Behavior Tree

# 首先，在UE编辑器中创建一个 Blackboard 资产和一个 Behavior Tree 资产。

# - **Blackboard**：定义需要存储的变量，例如目标位置（TargetLocation）。
# - **Behavior Tree**：定义AI行为逻辑，例如移动到目标位置。

# #### 2. 配置Blackboard

# 在 Blackboard 资产中添加一个名为 `TargetLocation` 的向量变量。

# #### 3. 配置Behavior Tree

# 在 Behavior Tree 资产中添加以下节点：

# - **Root**：行为树的根节点。
# - **Selector**：选择节点，用于选择要执行的子节点。
# - **Sequence**：序列节点，用于按顺序执行子节点。
# - **Move To**：移动节点，移动到 Blackboard 中的目标位置。

# 行为树结构如下：

# ```plaintext
# [Root]
#   └── [Selector]
#          └── [Sequence]
#                 ├── [Move To: TargetLocation]
#                 └── [Other Actions]
# ```

# #### 4. 创建AI控制器

# 创建一个自定义的 AI 控制器类来运行行为树。

# ```cpp
# // MyAIController.h
# #pragma once

# #include "CoreMinimal.h"
# #include "AIController.h"
# #include "MyAIController.generated.h"

# UCLASS()
# class MYGAME_API AMyAIController : public AAIController
# {
#     GENERATED_BODY()

# public:
#     virtual void BeginPlay() override;

# protected:
#     UPROPERTY(EditDefaultsOnly, Category = "AI")
#     UBehaviorTree* BehaviorTree;

#     UPROPERTY(EditDefaultsOnly, Category = "AI")
#     UBlackboardData* BlackboardData;
# };

# // MyAIController.cpp
# #include "MyAIController.h"
# #include "BehaviorTree/BlackboardComponent.h"
# #include "BehaviorTree/BehaviorTreeComponent.h"

# void AMyAIController::BeginPlay()
# {
#     Super::BeginPlay();

#     if (BehaviorTree && BlackboardData)
#     {
#         UseBlackboard(BlackboardData, BlackboardComponent);
#         RunBehaviorTree(BehaviorTree);

#         // 设置初始目标位置
#         FVector TargetLocation = FVector(100.0f, 200.0f, 300.0f);
#         BlackboardComponent->SetValueAsVector(TEXT("TargetLocation"), TargetLocation);
#     }
# }
# ```

# ### 解释

# 1. **Blackboard**：用于存储共享数据（例如目标位置）。
# 2. **Behavior Tree**：定义AI行为逻辑（例如移动到目标位置）。
# 3. **AI 控制器**：启动行为树并设置初始目标位置。

# 通过这种方式，Blackboard 可以在行为树的不同节点之间共享数据，使得AI逻辑更加灵活和可扩展。

# ### 调试和监控

# 在UE编辑器中，可以通过行为树编辑器和Blackboard调试器来监控和调试AI行为。这些工具提供了可视化界面，使开发者能够实时查看Blackboard变量的值和行为树的执行流程。

# ### 总结

# Blackboard 在Unreal Engine的行为树系统中扮演着关键角色，通过提供共享数据存储和访问机制，使得AI逻辑能够更加灵活和复杂。理解Blackboard的功能和使用方法，有助于开发高效和可维护的AI行为。
