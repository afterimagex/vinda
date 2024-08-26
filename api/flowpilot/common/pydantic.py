#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/1/11 17:25
@Author  : 
@File    : 
"""
from typing import Any, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    GenerateSchema,
    PrivateAttr,
    field_serializer,
    field_validator,
    model_serializer,
    model_validator,
)

# class ContextMixin(BaseModel):
#     """Mixin class for context and config"""

#     model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

#     # Pydantic has bug on _private_attr when using inheritance, so we use private_* instead
#     # - https://github.com/pydantic/pydantic/issues/7142
#     # - https://github.com/pydantic/pydantic/issues/7083
#     # - https://github.com/pydantic/pydantic/issues/7091

#     # Env/Role/Action will use this context as private context, or use self.context as public context
#     private_context: Optional[Context] = Field(default=None, exclude=True)
#     # Env/Role/Action will use this config as private config, or use self.context.config as public config
#     private_config: Optional[Config] = Field(default=None, exclude=True)

#     # Env/Role/Action will use this llm as private llm, or use self.context._llm instance
#     private_llm: Optional[BaseLLM] = Field(default=None, exclude=True)

#     @model_validator(mode="after")
#     def validate_context_mixin_extra(self):
#         self._process_context_mixin_extra()
#         return self

#     def _process_context_mixin_extra(self):
#         """Process the extra field"""
#         kwargs = self.model_extra or {}
#         self.set_context(kwargs.pop("context", None))
#         self.set_config(kwargs.pop("config", None))
#         self.set_llm(kwargs.pop("llm", None))

#     def set(self, k, v, override=False):
#         """Set attribute"""
#         if override or not self.__dict__.get(k):
#             self.__dict__[k] = v

#     def set_context(self, context: Context, override=True):
#         """Set context"""
#         self.set("private_context", context, override)

#     def set_config(self, config: Config, override=False):
#         """Set config"""
#         self.set("private_config", config, override)
#         if config is not None:
#             _ = self.llm  # init llm

#     def set_llm(self, llm: BaseLLM, override=False):
#         """Set llm"""
#         self.set("private_llm", llm, override)

#     @property
#     def config(self) -> Config:
#         """Role config: role config > context config"""
#         if self.private_config:
#             return self.private_config
#         return self.context.config

#     @config.setter
#     def config(self, config: Config) -> None:
#         """Set config"""
#         self.set_config(config)

#     @property
#     def context(self) -> Context:
#         """Role context: role context > context"""
#         if self.private_context:
#             return self.private_context
#         return Context()

#     @context.setter
#     def context(self, context: Context) -> None:
#         """Set context"""
#         self.set_context(context)

#     @property
#     def llm(self) -> BaseLLM:
#         """Role llm: if not existed, init from role.config"""
#         # print(f"class:{self.__class__.__name__}({self.name}), llm: {self._llm}, llm_config: {self._llm_config}")
#         if not self.private_llm:
#             self.private_llm = self.context.llm_with_cost_manager_from_llm_config(
#                 self.config.llm
#             )
#         return self.private_llm

#     @llm.setter
#     def llm(self, llm: BaseLLM) -> None:
#         """Set llm"""
#         self.private_llm = llm


class SerializationMixin(BaseModel, extra="forbid"):
    """
    PolyMorphic subclasses Serialization / Deserialization Mixin
    - First of all, we need to know that pydantic is not designed for polymorphism.
    - If Engineer is subclass of Role, it would be serialized as Role. If we want to serialize it as Engineer, we need
        to add `class name` to Engineer. So we need Engineer inherit SerializationMixin.

    More details:
    - https://docs.pydantic.dev/latest/concepts/serialization/
    - https://github.com/pydantic/pydantic/discussions/7008 discuss about avoid `__get_pydantic_core_schema__`
    """

    __is_polymorphic_base = False
    __subclasses_map__ = {}

    @model_serializer(mode="wrap")
    def __serialize_with_class_type__(self, default_serializer) -> Any:
        # default serializer, then append the `__module_class_name` field and return
        ret = default_serializer(self)
        ret["__module_class_name"] = (
            f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        )
        return ret

    @model_validator(mode="wrap")
    @classmethod
    def __convert_to_real_type__(cls, value: Any, handler):
        if isinstance(value, dict) is False:
            return handler(value)

        # it is a dict so make sure to remove the __module_class_name
        # because we don't allow extra keywords but want to ensure
        # e.g Cat.model_validate(cat.model_dump()) works
        class_full_name = value.pop("__module_class_name", None)

        # if it's not the polymorphic base we construct via default handler
        if not cls.__is_polymorphic_base:
            if class_full_name is None:
                return handler(value)
            elif str(cls) == f"<class '{class_full_name}'>":
                return handler(value)
            else:
                # f"Trying to instantiate {class_full_name} but this is not the polymorphic base class")
                pass

        # otherwise we lookup the correct polymorphic type and construct that
        # instead
        if class_full_name is None:
            raise ValueError("Missing __module_class_name field")

        class_type = cls.__subclasses_map__.get(class_full_name, None)

        if class_type is None:
            # TODO could try dynamic import
            raise TypeError(
                "Trying to instantiate {class_full_name}, which has not yet been defined!"
            )

        return class_type(**value)

    def __init_subclass__(cls, is_polymorphic_base: bool = False, **kwargs):
        cls.__is_polymorphic_base = is_polymorphic_base
        cls.__subclasses_map__[f"{cls.__module__}.{cls.__qualname__}"] = cls
        super().__init_subclass__(**kwargs)
