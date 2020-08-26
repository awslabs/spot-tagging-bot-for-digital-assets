# 数字资产盘活机器人

[English Version](./README.md)

数字资产盘活机器人是一个将机器学习应用于业务场景的解决方案，客户可以使用此解决方案中的机器人，对其上传至Amazon Web Services （AWS）云上的数字资产（例如，照片、PDF文档、视频等非结构化数据）进行知识标记。标记知识将有助于客户实现业务流程自动化。

此解决方案利用Amazon Simple Storage Service (Amazon S3) 和Amazon Elastic Compute Cloud (Amazon EC2) 的竞价型实例（Spot Instances），使客户可以安全的、低成本的使用批处理机器人来标记数字资产。机器人将所识别出的信息存储在客户私有的Amazon S3 存储桶中来保证数据安全性，机器人将运行在EC2竞价型实例中来节省计算成本。

此解决方案是一个开源框架，构建者可以通过创建自己的模型或机器人为本解决方案框架做出贡献。


- **适用区域:** cn-northwest-1(宁夏), cn-north-1(北京)
- **版本:** v1.0
- **预计部署时间:** 20min

如果您在部署过程中出现问题，可以通过 [GitHub Issues](https://github.com/aws-samples/spot-tag-bot-for-digital-assets/issues) 联系我们。

## 架构

您可以选择直接部署数字资产盘活机器人解决方案，以下是方案的架构图。

![Architect](assets/architect.png)

## 步骤1: 启动 CloudFormation 堆栈

此自动化 AWS CloudFormation 模板在 AWS Cloud 上部署 BigBlueButton 应用程序。

您负责运行此解决方案时使用的AWS服务的成本。 有关更多详细信息，请参见“费用”部分。 有关完整详细信息，请参阅此解决方案中将使用的每个AWS服务的定价页面。

1. 登录到AWS管理控制台，然后单击下面的按钮以启动 AWS CloudFormation 模板。

    [![Launch Stack](assets/launch-stack.png)](https://cn-northwest-1.console.amazonaws.cn/cloudformation/home?region=cn-northwest-1#/stacks/create/template?stackName=spot-bot&templateURL=https:%2F%2Faws-solutions-reference.s3.cn-north-1.amazonaws.com.cn%2Fspot-bot%2Fv1.0.0%2Fspot-bot-china.template)
    
2. 默认情况下，该模板在 AWS 宁夏区域启动。 要在其他AWS区域中启动该解决方案，请使用控制台导航栏中的区域选择器。

3. 在**创建堆栈**页面上，确认 **Amazon S3 URL** 文本框中显示正确的模板URL，然后选择**下一步**。

4. 在**指定堆栈详细信息**页面上，为解决方案堆栈分配名称。

5. 在**参数**下，查看模板的参数并根据需要进行修改。 此解决方案使用以下默认值。

2. 选择**下一步**。

3. 在**配置堆栈选项**页面上，选择“下一步”。

4. 在**审核**页面上，查看并确认设置。 确保选中确认模板将创建 AWS Identity and Access Management（IAM）资源的框。

5. 选择**创建堆栈**以部署堆栈。

您可以在AWS CloudFormation控制台的**状态**列中查看堆栈的状态。 您应该在大约20分钟内看到状态为CREATE_COMPLETE。

## 常见问题

**Q: 资产盘活机器人解决方案是如何运作的？**

资产盘活机器人解决方案包含一个AWS CloudFormation模版，帮助你在你的AWS账号中快速部署。这个模版会启动你部署本解决方案所需要的所有资源和权限设置。
当模版部署后，你可以指定你所需要盘活的数据资产的S3路径及对应所需要启动的机器人。资产盘活机器人解决方案支持很多的数据资产类型，包含文本，视频，图片等。指定的机器人在启动后会根据当前S3的内容生成一份任务列表，列表中包含了需要处理的数字资产，比如1000个需要打标签的视频。具体的任务会被分段（Batch），然后多个机器人实例会处理各自的任务段，如果一共有10个机器人，每个片段可能包括100个视频。这些机器人实例都是运行在Spot Instance上的，所以在计算上具有很高的性价比。机器人处理完当前任务后会将结果写入Elastic Search和S3。如果某个机器人实例发生异常，则相应的任务会交给其他的机器人实例来重做。客户可以通过Elastic Search查询任务的结果，并且了解整个任务的执行状态。

每个机器人都是由两层构成的，一层实现的业务需求，比如OCR机器人可以完成OCR任务，但是具体的OCR任务可能需要多个模型协作完成，比如一个模型把文本部分框出来，另一个模型只负责识别框好的文字，这些模型是第二层，为业务层提供能力支持。

**Q: 我能使用自己的数据进行二次训练吗？**

是的，资产盘活机器人解决方案中带有一个基于容器的训练框架。用户可以使用AWS Sagemaker或者其它Notebook托管服务来打开训练框架软件，并导入自己标注过的数据进行训练。训练后的结果用户可以导出到资产盘活机器人解决方案的机器人框架中。资产盘活机器人解决方案将使用二次训练后的模型进行推理，以更好地适应不同用户的需求。

**Q: CloudFormation部署失败了，如何查看失败的原因?**

您可在查看[AWS CloudFormation 疑难解答](https://docs.aws.amazon.com/zh_cn/AWSCloudFormation/latest/UserGuide/troubleshooting.html)和[AWS CloudFormation 常见问题](https://aws.amazon.com/cn/cloudformation/faqs/?nc1=h_ls)找到有关 AWS CloudFormation 的一般性问题。
如果您无法自行解决，可通过 [GitHub Issues](https://github.com/aws-samples/spot-tag-bot-for-digital-assets/issues)
联系我们。

**资产盘活机器人解决方案支持在哪些区域运行？**

您可以部署资产盘活机器人解决方案到由西云数据运营的AWS(宁夏)区域和由光环新网运营的AWS(北京)区域
