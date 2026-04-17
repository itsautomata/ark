"""FLAIRR-TS test fixture. documented hallucinated citation ground truth.

paper: FLAIRR-TS (Jalori, Verma, Arik), EMNLP 2025 Findings, arxiv:2508.19279
source for ground truth: Sakai et al. 2026 "HalluCitation Matters" (arXiv:2601.18724)

the paper cites a fabricated TEMPO reference. the citation claims arXiv:2405.18384
is about temporal representation prompting in LLMs. that arxiv ID is real but points
to "Decentralized Picosecond Synchronization for Distributed Wireless Systems",
a wireless engineering paper, completely unrelated.

this is an arxiv ID hijack. ark should catch it as metadata_mismatch.

observations while extracting the references:
- several entries have leftover LLM artifacts: "Placeholder entry", "Placeholder
  'tang-etal-2024-enrichingprompts' resolved", "Anticipated for NeurIPS 2024".
  these are signatures of an AI-assisted reference list that was not cleaned up.
- the TEMPO citation is the one documented as outright fake. others may also
  be suspicious but we only mark what has been verified by the HalluCitation audit.
"""

from ark.models import Paper, Reference

ABSTRACT = (
    "Time series Forecasting with large language models (LLMs) requires bridging "
    "numerical patterns and natural language. Effective forecasting on LLM often "
    "relies on extensive pre-processing and fine-tuning. Recent studies show that "
    "a frozen LLM can rival specialized forecasters when supplied with a carefully "
    "engineered natural-language prompt, but crafting such a prompt for each task "
    "is itself onerous and ad-hoc. We introduce FLAIRR-TS, a test-time prompt "
    "optimization framework that utilizes an agentic system: a Forecaster-agent "
    "generates forecasts using an initial prompt, which is then refined by a refiner "
    "agent, informed by past outputs and retrieved analogs. This adaptive prompting "
    "generalizes across domains using creative prompt templates and generates "
    "high-quality forecasts without intermediate code generation. Experiments on "
    "benchmark datasets show improved accuracy over static prompting and "
    "retrieval-augmented baselines, approaching the performance of specialized "
    "prompts. FLAIRR-TS provides a practical alternative to tuning, achieving "
    "strong performance via its agentic approach to adaptive prompt refinement "
    "and retrieval."
)

PAPER = Paper(
    title="FLAIRR-TS: Forecasting LLM-Agents with Iterative Refinement and Retrieval for Time Series",
    authors=["Gunjan Jalori", "Preetika Verma", "Sercan O. Arik"],
    year=2025,
    abstract=ABSTRACT,
    references=[
        # 0
        Reference(
            raw="Zhaofeng Chen and others. 2025. SETS: Self-verification and self-correction for improved test-time scaling. Anticipated for ICML. Placeholder entry.",
            title="SETS: Self-verification and self-correction for improved test-time scaling",
            authors=["Zhaofeng Chen"],
            year=2025,
            arxiv_id=None,
        ),
        # 1
        Reference(
            raw="Vijay Ekambaram, Arindam Jati, Pankaj Dayama, Sumanta Mukherjee, Nam H. Nguyen, Wesley M. Gifford, Chandra Reddy, and Jayant Kalagnanam. 2024. Tiny time mixers (ttms): Fast pre-trained models for enhanced zero/few-shot forecasting of multivariate time series. arXiv:2401.03955.",
            title="Tiny time mixers (ttms): Fast pre-trained models for enhanced zero/few-shot forecasting of multivariate time series",
            authors=["Vijay Ekambaram", "Arindam Jati", "Pankaj Dayama", "Sumanta Mukherjee",
                     "Nam H. Nguyen", "Wesley M. Gifford", "Chandra Reddy", "Jayant Kalagnanam"],
            year=2024,
            arxiv_id="2401.03955",
        ),
        # 2
        Reference(
            raw="Nate Gruver, Marc Finzi, Shikai Qiu, and Andrew Gordon Wilson. 2023. Large language models are zero-shot time series forecasters. NeurIPS 2023. arXiv:2310.07820.",
            title="Large language models are zero-shot time series forecasters",
            authors=["Nate Gruver", "Marc Finzi", "Shikai Qiu", "Andrew Gordon Wilson"],
            year=2023,
            arxiv_id="2310.07820",
        ),
        # 3
        Reference(
            raw="Seungone Han, Peiyuan Liao, Poming P. Chiu, Jennifer Hobbs, Sungtae An, Min hwan Oh, Vikas K. Garg, Caiming Xiong, and Yoonkey Kim. 2023. Retrieval augmented time series forecasting. NeurIPS 2023. arXiv:2310.16227.",
            title="Retrieval augmented time series forecasting",
            authors=["Seungone Han", "Peiyuan Liao", "Poming P. Chiu", "Jennifer Hobbs",
                     "Sungtae An", "Min hwan Oh", "Vikas K. Garg", "Caiming Xiong", "Yoonkey Kim"],
            year=2023,
            arxiv_id="2310.16227",
        ),
        # 4
        Reference(
            raw="Ming Jin, Shiyu Wang, Lintao Ma, Zhixuan Chu, James Y. Zhang, Xiaoming Shi, Pin-Yu Chen, Yuxuan Liang, Yuan-Fang Li, Shirui Pan, and Qingsong Wen. 2024. Time-LLM: Time series forecasting by reprogramming large language models. ICLR. arXiv:2310.01728.",
            title="Time-LLM: Time series forecasting by reprogramming large language models",
            authors=["Ming Jin", "Shiyu Wang", "Lintao Ma", "Zhixuan Chu", "James Y. Zhang",
                     "Xiaoming Shi", "Pin-Yu Chen", "Yuxuan Liang", "Yuan-Fang Li",
                     "Shirui Pan", "Qingsong Wen"],
            year=2024,
            arxiv_id="2310.01728",
        ),
        # 5
        Reference(
            raw="Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, Naman Goyal, Heinrich Kuttler, Mike Lewis, Wen tau Yih, Tim Rocktaschel, Sebastian Riedel, and Douwe Kiela. 2020. Retrieval-augmented generation for knowledge-intensive NLP tasks. NeurIPS 2020.",
            title="Retrieval-augmented generation for knowledge-intensive NLP tasks",
            authors=["Patrick Lewis", "Ethan Perez", "Aleksandra Piktus", "Fabio Petroni",
                     "Vladimir Karpukhin", "Naman Goyal", "Heinrich Kuttler", "Mike Lewis",
                     "Wen tau Yih", "Tim Rocktaschel", "Sebastian Riedel", "Douwe Kiela"],
            year=2020,
            arxiv_id=None,
        ),
        # 6
        Reference(
            raw="Haoxin Liu, Zhiyuan Zhao, Jindong Wang, Harshavardhan Kamarthi, and B. Aditya Prakash. 2024. Lstprompt: Large language models as zero-shot time series forecasters by long-short-term prompting. arXiv:2402.16132.",
            title="Lstprompt: Large language models as zero-shot time series forecasters by long-short-term prompting",
            authors=["Haoxin Liu", "Zhiyuan Zhao", "Jindong Wang", "Harshavardhan Kamarthi",
                     "B. Aditya Prakash"],
            year=2024,
            arxiv_id="2402.16132",
        ),
        # 7
        Reference(
            raw="Aman Madaan, Niket Tandon, Prakhar Gupta, Skyler Hallinan, Luyu Gao, Sarah Wiegreffe, Uri Alon, Nouha Dziri, Shrimai Prabhumoye, Yiming Yang, Shashank Gupta, Bodhisattwa Prasad Majumder, Katherine Hermann, Sean Welleck, Amir Yazdanbakhsh, and Peter Clark. 2023. Self-Refine: Iterative refinement with Self-Feedback. arXiv:2303.17651.",
            title="Self-Refine: Iterative refinement with Self-Feedback",
            authors=["Aman Madaan", "Niket Tandon", "Prakhar Gupta", "Skyler Hallinan",
                     "Luyu Gao", "Sarah Wiegreffe", "Uri Alon", "Nouha Dziri",
                     "Shrimai Prabhumoye", "Yiming Yang", "Shashank Gupta",
                     "Bodhisattwa Prasad Majumder", "Katherine Hermann", "Sean Welleck",
                     "Amir Yazdanbakhsh", "Peter Clark"],
            year=2023,
            arxiv_id="2303.17651",
        ),
        # 8
        Reference(
            raw="Yuqi Nie, Nam H. Nguyen, Phanwadee Sinthong, and Jayant Kalagnanam. 2023. A time series is worth 64 words: Long-term forecasting with transformers. arXiv:2211.14730.",
            title="A time series is worth 64 words: Long-term forecasting with transformers",
            authors=["Yuqi Nie", "Nam H. Nguyen", "Phanwadee Sinthong", "Jayant Kalagnanam"],
            year=2023,
            arxiv_id="2211.14730",
        ),
        # 9
        Reference(
            raw="Peisong Niu, Tian Zhou, Xue Wang, Liang Sun, and Rong Jin. 2024. Understanding the role of textual prompts in llm for time series forecasting: an adapter view. arXiv:2311.14782.",
            title="Understanding the role of textual prompts in llm for time series forecasting: an adapter view",
            authors=["Peisong Niu", "Tian Zhou", "Xue Wang", "Liang Sun", "Rong Jin"],
            year=2024,
            arxiv_id="2311.14782",
        ),
        # 10
        Reference(
            raw="Pranab Sahoo, Ayush Kumar Singh, Sriparna Saha, Vinija Jain, Samrat Mondal, and Aman Chadha. 2025. A systematic survey of prompt engineering in large language models: Techniques and applications. arXiv:2402.07927.",
            title="A systematic survey of prompt engineering in large language models: Techniques and applications",
            authors=["Pranab Sahoo", "Ayush Kumar Singh", "Sriparna Saha", "Vinija Jain",
                     "Samrat Mondal", "Aman Chadha"],
            year=2025,
            arxiv_id="2402.07927",
        ),
        # 11
        Reference(
            raw="Jingyi Tang, Zongyao Zhang, Daksh Minhas, Chengzhang Li, Haomin Chen, Minghuan Tan, Chetan Shah, and Joyce C. Ho. 2024. Prompting medical large vision-language models to diagnose pathologies by visual question answering. arXiv:2407.21368.",
            title="Prompting medical large vision-language models to diagnose pathologies by visual question answering",
            authors=["Jingyi Tang", "Zongyao Zhang", "Daksh Minhas", "Chengzhang Li",
                     "Haomin Chen", "Minghuan Tan", "Chetan Shah", "Joyce C. Ho"],
            year=2024,
            arxiv_id="2407.21368",
        ),
        # 12
        Reference(
            raw="Yu-Hsiang Lin Wan, Akshita Agrawal, Chiyu Max Jiang, Eunsol Choi, and Graham Neubig. 2024. Self-supervised prompting for cross-lingual in-context learning in low-resource languages. arXiv:2406.18880.",
            title="Self-supervised prompting for cross-lingual in-context learning in low-resource languages",
            authors=["Yu-Hsiang Lin Wan", "Akshita Agrawal", "Chiyu Max Jiang",
                     "Eunsol Choi", "Graham Neubig"],
            year=2024,
            arxiv_id="2406.18880",
        ),
        # 13
        Reference(
            raw="Hao Xue and Flora D. Salim. 2024. Promptcast: A new prompt-based learning paradigm for time series forecasting. IEEE TKDE, 36(11):6851-6864.",
            title="Promptcast: A new prompt-based learning paradigm for time series forecasting",
            authors=["Hao Xue", "Flora D. Salim"],
            year=2024,
            arxiv_id=None,
        ),
        # 14
        Reference(
            raw="Ailing Zeng, Muxi Chen, Lei Zhang, and Qiang Xu. 2022. Are transformers effective for time series forecasting? arXiv:2205.13504.",
            title="Are transformers effective for time series forecasting?",
            authors=["Ailing Zeng", "Muxi Chen", "Lei Zhang", "Qiang Xu"],
            year=2022,
            arxiv_id="2205.13504",
        ),
        # 15
        Reference(
            raw="Haoyi Zhou, Shanghang Zhang, Jieqi Peng, Shuai Zhang, Jianxin Li, Hui Xiong, and Wancai Zhang. 2021. Informer: Beyond efficient transformer for long sequence time-series forecasting. AAAI 2021, 35, 11106-11115.",
            title="Informer: Beyond efficient transformer for long sequence time-series forecasting",
            authors=["Haoyi Zhou", "Shanghang Zhang", "Jieqi Peng", "Shuai Zhang",
                     "Jianxin Li", "Hui Xiong", "Wancai Zhang"],
            year=2021,
            arxiv_id=None,
        ),
        # 16
        Reference(
            raw="Tian Zhou, Ziqing Ma, Qingsong Wen, Xue Wang, Liang Sun, and Rong Jin. 2022. FEDformer: Frequency enhanced decomposed transformer for long-term series forecasting. ICML 2022, 162, 27268-27286.",
            title="FEDformer: Frequency enhanced decomposed transformer for long-term series forecasting",
            authors=["Tian Zhou", "Ziqing Ma", "Qingsong Wen", "Xue Wang",
                     "Liang Sun", "Rong Jin"],
            year=2022,
            arxiv_id=None,
        ),
        # 17 - THE FAKE ONE
        Reference(
            raw="Wendi Zhou, Xiao Li, Lin Geng Foo, Yitan Wang, Harold Soh, Caiming Xiong, and Yoonkey Kim. 2024. TEMPO: Temporal representation prompting for large language models in time-series forecasting. arXiv:2405.18384.",
            title="TEMPO: Temporal representation prompting for large language models in time-series forecasting",
            authors=["Wendi Zhou", "Xiao Li", "Lin Geng Foo", "Yitan Wang",
                     "Harold Soh", "Caiming Xiong", "Yoonkey Kim"],
            year=2024,
            arxiv_id="2405.18384",
        ),
    ],
)

# only index 17 (TEMPO) is documented ground truth as a fake.
# the Sakai et al. audit surfaced this specific reference.
EXPECTED_VERDICTS = {
    17: "metadata_mismatch",
}
